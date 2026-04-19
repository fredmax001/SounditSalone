"""
CLI Commands for Sound It
"""
import click
import sys
from typing import Optional
from .api_client import SoundItAPI, APIError
from .config import ConfigManager, CLIConfig
from .formatters import output, format_summary, format_user, format_event


pass_api = click.make_pass_decorator(SoundItAPI, ensure=True)


# ============ CONFIG GROUP ============

@click.group()
@click.option('--api-url', envvar='SOUNDIT_API_URL', help='API base URL')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'csv']), help='Output format')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, api_url, output_format, debug):
    """Sound It CLI - Manage your music events platform"""
    # Load config
    config = ConfigManager.get_config()
    
    # Override with CLI options
    if api_url:
        config.api_base_url = api_url
    if output_format:
        config.default_format = output_format
    
    # Save config updates
    ConfigManager.save_config(config)
    
    # Initialize API client
    ctx.obj = SoundItAPI(config)
    ctx.ensure_object(dict)
    ctx.obj['format'] = output_format
    ctx.obj['debug'] = debug


# ============ AUTH COMMANDS ============

@cli.group()
def auth():
    """Authentication commands"""
    pass


@auth.command()
@click.option('--email', '-e', prompt=True, help='Email address')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
def login(email, password):
    """Login to Sound It API"""
    try:
        api = SoundItAPI()
        result = api.login(email, password)
        
        # Save tokens
        config = ConfigManager.get_config()
        config.access_token = result.get('access_token')
        config.refresh_token = result.get('refresh_token')
        ConfigManager.save_config(config)
        
        click.echo(click.style("✓ Login successful!", fg="green"))
        click.echo(f"Welcome, {result.get('user', {}).get('email', 'User')}!")
        
    except APIError as e:
        click.echo(click.style(f"✗ Login failed: {e.message}", fg="red"))
        sys.exit(1)


@auth.command()
def logout():
    """Logout and clear credentials"""
    ConfigManager.clear_config()
    click.echo(click.style("✓ Logged out successfully", fg="green"))


@auth.command()
@pass_api
def me(api):
    """Show current user info"""
    try:
        user = api.get_me()
        click.echo(format_user(user))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@auth.command()
def status():
    """Check authentication status"""
    config = ConfigManager.get_config()
    if config.access_token:
        click.echo(click.style("✓ Logged in", fg="green"))
        click.echo(f"API URL: {config.api_base_url}")
    else:
        click.echo(click.style("✗ Not logged in", fg="red"))
        click.echo("Run 'soundit auth login' to authenticate")


# ============ USER COMMANDS ============

@cli.group()
def users():
    """User management commands"""
    pass


@users.command(name="list")
@click.option('--role', type=click.Choice(['user', 'business', 'artist', 'admin']), 
              help='Filter by role')
@click.option('--status', type=click.Choice(['active', 'inactive', 'suspended']), 
              help='Filter by status')
@click.option('--limit', '-l', default=20, help='Number of results')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def list_users(api, role, status, limit, output_format):
    """List users"""
    try:
        users = api.list_users(limit=limit, role=role, status=status)
        columns = ['id', 'first_name', 'last_name', 'email', 'role', 'status', 'created_at']
        output(users, output_format or 'table', columns)
        click.echo(f"\nTotal: {len(users)} users")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@users.command()
@click.argument('user_id', type=int)
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def get(api, user_id, output_format):
    """Get user details"""
    try:
        user = api.get_user(user_id)
        if output_format == 'json':
            output(user, 'json')
        else:
            click.echo(format_user(user))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@users.command()
@click.argument('user_id', type=int)
@click.option('--role', type=click.Choice(['user', 'business', 'artist', 'admin', 'super_admin']))
@click.option('--status', type=click.Choice(['active', 'inactive', 'suspended']))
@click.option('--verified/--not-verified', default=None, help='Set verified status')
@pass_api
def update(api, user_id, role, status, verified):
    """Update user"""
    try:
        data = {}
        if role:
            data['role'] = role
        if status:
            data['status'] = status
        if verified is not None:
            data['is_verified'] = verified
        
        if not data:
            click.echo(click.style("No changes specified", fg="yellow"))
            return
        
        user = api.update_user(user_id, data)
        click.echo(click.style("✓ User updated successfully", fg="green"))
        click.echo(format_user(user))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@users.command()
@click.argument('user_id', type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this user?")
@pass_api
def delete(api, user_id):
    """Delete user"""
    try:
        api.delete_user(user_id)
        click.echo(click.style(f"✓ User {user_id} deleted", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


# ============ EVENT COMMANDS ============

@cli.group()
def events():
    """Event management commands"""
    pass


@events.command(name="list")
@click.option('--status', type=click.Choice(['draft', 'pending', 'approved', 'rejected', 'cancelled']),
              help='Filter by status')
@click.option('--city', help='Filter by city')
@click.option('--limit', '-l', default=20, help='Number of results')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def list_events(api, status, city, limit, output_format):
    """List events"""
    try:
        events = api.list_events(limit=limit, status=status, city=city)
        columns = ['id', 'title', 'status', 'start_date', 'city', 'venue_name']
        output(events, output_format or 'table', columns)
        click.echo(f"\nTotal: {len(events)} events")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@events.command()
@click.argument('event_id', type=int)
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def get(api, event_id, output_format):
    """Get event details"""
    try:
        event = api.get_event(event_id)
        if output_format == 'json':
            output(event, 'json')
        else:
            click.echo(format_event(event))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@events.command()
@click.argument('event_id', type=int)
@pass_api
def approve(api, event_id):
    """Approve an event"""
    try:
        event = api.approve_event(event_id)
        click.echo(click.style(f"✓ Event {event_id} approved", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@events.command()
@click.argument('event_id', type=int)
@click.option('--reason', '-r', required=True, help='Rejection reason')
@pass_api
def reject(api, event_id, reason):
    """Reject an event"""
    try:
        event = api.reject_event(event_id, reason)
        click.echo(click.style(f"✓ Event {event_id} rejected", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@events.command()
@click.argument('event_id', type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this event?")
@pass_api
def delete(api, event_id):
    """Delete event"""
    try:
        api.delete_event(event_id)
        click.echo(click.style(f"✓ Event {event_id} deleted", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


# ============ VENUE COMMANDS ============

@cli.group()
def venues():
    """Venue/Club management commands"""
    pass


@venues.command(name="list")
@click.option('--city', help='Filter by city')
@click.option('--limit', '-l', default=20, help='Number of results')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def list_venues(api, city, limit, output_format):
    """List venues"""
    try:
        venues = api.list_venues(limit=limit, city=city)
        columns = ['id', 'name', 'city', 'address', 'phone', 'is_active']
        output(venues, output_format or 'table', columns)
        click.echo(f"\nTotal: {len(venues)} venues")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@venues.command()
@click.argument('venue_id', type=int)
@pass_api
def get(api, venue_id):
    """Get venue details"""
    try:
        venue = api.get_venue(venue_id)
        output(venue, 'table')
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


# ============ ADMIN COMMANDS ============

@cli.group()
def admin():
    """Admin commands"""
    pass


@admin.command()
@pass_api
def stats(api):
    """Show dashboard statistics"""
    try:
        stats = api.get_dashboard_stats()
        click.echo(format_summary(stats))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@admin.command()
@pass_api
def pending(api):
    """Show pending actions"""
    try:
        actions = api.get_pending_actions()
        if actions.get('actions'):
            columns = ['id', 'type', 'title', 'created_at', 'entity_type']
            output(actions['actions'], 'table', columns)
            click.echo(f"\nTotal pending: {actions.get('total_count', 0)}")
        else:
            click.echo("No pending actions")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@admin.command(name="verifications")
@click.option('--status', default='pending', type=click.Choice(['pending', 'approved', 'rejected']))
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def list_verifications(api, status, output_format):
    """List verification requests"""
    try:
        verifications = api.get_verification_requests(status)
        columns = ['id', 'type', 'entity_name', 'submitted_by', 'submitted_at', 'status']
        output(verifications, output_format or 'table', columns)
        click.echo(f"\nTotal: {len(verifications)} verifications")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@admin.command()
@click.argument('verification_id', type=int)
@click.option('--notes', '-n', help='Approval notes')
@pass_api
def approve_verification(api, verification_id, notes):
    """Approve a verification request"""
    try:
        result = api.approve_verification(verification_id, notes)
        click.echo(click.style(f"✓ Verification {verification_id} approved", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@admin.command()
@click.argument('verification_id', type=int)
@click.option('--reason', '-r', required=True, help='Rejection reason')
@pass_api
def reject_verification(api, verification_id, reason):
    """Reject a verification request"""
    try:
        result = api.reject_verification(verification_id, reason)
        click.echo(click.style(f"✓ Verification {verification_id} rejected", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


# ============ ORDER COMMANDS ============

@cli.group()
def orders():
    """Order management commands"""
    pass


@orders.command(name="list")
@click.option('--status', type=click.Choice(['pending', 'completed', 'failed', 'refunded']))
@click.option('--limit', '-l', default=20, help='Number of results')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']))
@pass_api
def list_orders(api, status, limit, output_format):
    """List orders"""
    try:
        orders = api.list_orders(limit=limit, status=status)
        columns = ['id', 'user_id', 'event_id', 'total_amount', 'status', 'created_at']
        output(orders, output_format or 'table', columns)
        click.echo(f"\nTotal: {len(orders)} orders")
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@orders.command()
@click.argument('order_id', type=int)
@pass_api
def get(api, order_id):
    """Get order details"""
    try:
        order = api.get_order(order_id)
        output(order, 'table')
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


@orders.command()
@click.argument('order_id', type=int)
@click.option('--reason', '-r', required=True, help='Refund reason')
@pass_api
def refund(api, order_id, reason):
    """Refund an order"""
    try:
        result = api.refund_order(order_id, reason)
        click.echo(click.style(f"✓ Order {order_id} refunded", fg="green"))
    except APIError as e:
        click.echo(click.style(f"✗ Error: {e.message}", fg="red"))
        sys.exit(1)


# Entry point
def main():
    cli()
