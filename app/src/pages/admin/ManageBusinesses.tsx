import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/store/authStore';
import { API_BASE_URL } from '@/config/api';
import { toast } from 'sonner';
import { 
  Building2, Search, Check, Ban, Trash2, Loader2, ShieldCheck, Mail, Calendar, MapPin, Star
} from 'lucide-react';

interface BusinessUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: string;
  status: string;
  is_verified: boolean;
  is_featured?: boolean;
  venue_type?: string;
  city?: string;
  created_at?: string;
}

export default function ManageBusinesses() {
  const { session } = useAuthStore();
  const [businesses, setBusinesses] = useState<BusinessUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadBusinesses = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users?role=venue`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        const list = Array.isArray(data) ? data : (data.users || []);
        setBusinesses(list);
      } else {
        toast.error('Failed to load businesses');
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to connect to API');
    } finally {
      setLoading(false);
    }
  }, [session]);

  useEffect(() => {
    loadBusinesses();
  }, [loadBusinesses]);

  const handleVerify = async (id: number) => {
    setActionLoading(`verify-${id}`);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users/${id}/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: 'business' })
      });
      if (res.ok) {
        toast.success('Business verified successfully');
        loadBusinesses();
      } else {
        toast.error('Failed to verify business');
      }
    } catch (error) {
      toast.error('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuspend = async (id: number) => {
    if (!confirm('Are you sure you want to suspend this business?')) return;
    setActionLoading(`suspend-${id}`);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users/${id}/suspend`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (res.ok) {
        toast.success('Business account suspended');
        loadBusinesses();
      } else {
        toast.error('Failed to suspend account');
      }
    } catch (error) {
      toast.error('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to permanently delete this business account?')) return;
    setActionLoading(`delete-${id}`);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`
        }
      });
      if (res.ok) {
        toast.success('Business account deleted');
        loadBusinesses();
      } else {
        toast.error('Failed to delete account');
      }
    } catch (error) {
      toast.error('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleFeature = async (id: number, currentStatus: boolean) => {
    if (!session?.access_token) return;
    
    setActionLoading(`feature-${id}`);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users/${id}/feature`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_featured: !currentStatus })
      });

      if (res.ok) {
        toast.success(currentStatus ? 'Business unfeatured successfully' : 'Business featured successfully');
        setBusinesses(businesses.map(b => 
          b.id === id ? { ...b, is_featured: !currentStatus } : b
        ));
      } else {
        toast.error('Failed to update feature status');
      }
    } catch (error) {
      console.error('Error updating feature status:', error);
      toast.error('Network error. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const filteredBusinesses = businesses.filter(biz => {
    const term = searchQuery.toLowerCase();
    return (
      biz.first_name?.toLowerCase().includes(term) ||
      biz.last_name?.toLowerCase().includes(term) ||
      biz.email?.toLowerCase().includes(term) ||
      biz.city?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6 text-foreground">
      <div>
        <h1 className="text-2xl font-bold text-white">Business Management</h1>
        <p className="text-gray-400 mt-1">Review and manage platform businesses, vendors, and venue profiles</p>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search businesses by organization name, email, or city..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-foreground placeholder-gray-500 focus:border-[#FFC107] focus:outline-none"
          />
        </div>
        <button
          onClick={loadBusinesses}
          className="flex items-center gap-2 px-4 py-2 bg-muted border border-border rounded-lg hover:bg-muted text-gray-300 transition-colors"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 text-[#FFC107] animate-spin" />
        </div>
      ) : filteredBusinesses.length === 0 ? (
        <div className="text-center py-12 text-gray-500 bg-card border border-border rounded-xl">
          <Building2 className="w-12 h-12 mx-auto mb-3 opacity-30 text-[#FFC107]" />
          <p>No businesses found</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="text-left text-gray-400 text-sm font-medium p-4">Business</th>
                  <th className="text-left text-gray-400 text-sm font-medium p-4">Contact & Location</th>
                  <th className="text-left text-gray-400 text-sm font-medium p-4">Status</th>
                  <th className="text-left text-gray-400 text-sm font-medium p-4">Joined</th>
                  <th className="text-right text-gray-400 text-sm font-medium p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredBusinesses.map((biz) => (
                  <tr key={biz.id} className="border-b border-border last:border-0 hover:bg-muted/20">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-[#FFC107]/10 flex items-center justify-center font-bold text-white text-lg">
                          <Building2 className="w-5 h-5 text-[#FFC107]" />
                        </div>
                        <div>
                          <p className="text-white font-semibold flex items-center gap-2">
                            {biz.first_name} {biz.last_name}
                            {biz.is_featured && <Star className="w-3 h-3 text-[#FFC107] fill-[#FFC107]" />}
                          </p>
                          <span className="text-xs text-[#FFC107] capitalize font-medium">{biz.venue_type || biz.role}</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 space-y-1">
                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <Mail className="w-4 h-4 text-gray-500" />
                        <span>{biz.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <span className="capitalize">{biz.city || 'Freetown'}</span>
                      </div>
                    </td>
                    <td className="p-4 space-y-1.5">
                      <div className="flex gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          biz.status === 'active' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {biz.status}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold flex items-center gap-1 ${
                          biz.is_verified 
                            ? 'bg-blue-500/20 text-blue-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {biz.is_verified && <ShieldCheck className="w-3.5 h-3.5" />}
                          {biz.is_verified ? 'Verified' : 'Pending'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-gray-400 text-sm">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-600" />
                        <span>{biz.created_at ? new Date(biz.created_at).toLocaleDateString() : '-'}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleFeature(biz.id, !!biz.is_featured)}
                          disabled={actionLoading === `feature-${biz.id}`}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50 ${
                            biz.is_featured 
                              ? 'bg-[#FFC107]/20 text-[#FFC107] hover:bg-[#FFC107]/30' 
                              : 'bg-background hover:bg-muted text-gray-400 hover:text-white border border-border'
                          }`}
                          title="Feature Business"
                        >
                          {actionLoading === `feature-${biz.id}` ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Star className={`w-3.5 h-3.5 ${biz.is_featured ? 'fill-[#FFC107]' : ''}`} />}
                          {biz.is_featured ? 'Featured' : 'Feature'}
                        </button>
                        {!biz.is_verified && (
                          <button
                            onClick={() => handleVerify(biz.id)}
                            disabled={actionLoading === `verify-${biz.id}`}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 hover:bg-green-500/20 rounded-lg text-green-400 text-xs font-semibold transition-colors disabled:opacity-50"
                            title="Verify Business"
                          >
                            {actionLoading === `verify-${biz.id}` ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                            Verify
                          </button>
                        )}
                        <button
                          onClick={() => handleSuspend(biz.id)}
                          disabled={actionLoading === `suspend-${biz.id}`}
                          className="p-2 hover:bg-yellow-500/10 rounded-lg text-yellow-400 transition-colors disabled:opacity-50"
                          title="Suspend"
                        >
                          {actionLoading === `suspend-${biz.id}` ? <Loader2 className="w-4.5 h-4.5 animate-spin" /> : <Ban className="w-4.5 h-4.5" />}
                        </button>
                        <button
                          onClick={() => handleDelete(biz.id)}
                          disabled={actionLoading === `delete-${biz.id}`}
                          className="p-2 hover:bg-red-500/10 rounded-lg text-red-400 transition-colors disabled:opacity-50"
                          title="Delete Account"
                        >
                          {actionLoading === `delete-${biz.id}` ? <Loader2 className="w-4.5 h-4.5 animate-spin" /> : <Trash2 className="w-4.5 h-4.5" />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
