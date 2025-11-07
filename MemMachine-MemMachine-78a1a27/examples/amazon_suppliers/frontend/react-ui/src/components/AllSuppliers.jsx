import { useState, useEffect } from 'react';
import { Database, Search, Loader2, ChevronDown, ChevronUp, Building2, User, Mail, Phone, MapPin, Package, Calendar } from 'lucide-react';
import { supplierApi } from '../services/api';

function AllSuppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSuppliers, setExpandedSuppliers] = useState({});
  const [sortBy, setSortBy] = useState('supplier_id');
  const [sortOrder, setSortOrder] = useState('asc');

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async (search = null) => {
    setLoading(true);
    setError(null);
    try {
      const response = await supplierApi.listSuppliers(search);
      setSuppliers(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error loading suppliers');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadSuppliers(searchTerm || null);
  };

  const toggleSupplier = (supplierId) => {
    setExpandedSuppliers((prev) => ({
      ...prev,
      [supplierId]: !prev[supplierId],
    }));
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const sortedSuppliers = [...suppliers].sort((a, b) => {
    const aVal = a[sortBy] || '';
    const bVal = b[sortBy] || '';
    const comparison = String(aVal).localeCompare(String(bVal), undefined, { numeric: true });
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="card-header">All Suppliers</h2>
            <p className="text-gray-600 mt-1">
              View and manage all supplier profiles in the CRM database
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-100 px-4 py-2 rounded-lg">
            <Database className="w-4 h-4" />
            <span className="font-semibold">{suppliers.length} Suppliers</span>
          </div>
        </div>

        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Supplier ID, Company Name, or Contact..."
              className="input-field flex-1"
            />
            <button
              type="submit"
              disabled={loading}
              className="btn-secondary flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Search
            </button>
            {searchTerm && (
              <button
                type="button"
                onClick={() => {
                  setSearchTerm('');
                  loadSuppliers();
                }}
                className="btn-secondary"
              >
                Clear
              </button>
            )}
          </div>
        </form>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3 shadow-soft">
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
            <span className="ml-3 text-gray-600 font-medium">Loading suppliers...</span>
          </div>
        ) : sortedSuppliers.length === 0 ? (
          <div className="text-center py-12">
            <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">No suppliers found</p>
            <p className="text-sm text-gray-500 mt-1">
              {searchTerm ? 'Try a different search term' : 'Add suppliers using the CRM tab'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Sort controls */}
            <div className="flex items-center gap-2 text-xs text-gray-600 mb-4">
              <span className="font-semibold">Sort by:</span>
              <button
                onClick={() => handleSort('supplier_id')}
                className={`px-3 py-1 rounded ${sortBy === 'supplier_id' ? 'bg-brand-100 text-brand-700 font-semibold' : 'hover:bg-gray-100'}`}
              >
                ID {sortBy === 'supplier_id' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                onClick={() => handleSort('company_name')}
                className={`px-3 py-1 rounded ${sortBy === 'company_name' ? 'bg-brand-100 text-brand-700 font-semibold' : 'hover:bg-gray-100'}`}
              >
                Company {sortBy === 'company_name' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                onClick={() => handleSort('status')}
                className={`px-3 py-1 rounded ${sortBy === 'status' ? 'bg-brand-100 text-brand-700 font-semibold' : 'hover:bg-gray-100'}`}
              >
                Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
            </div>

            {/* Supplier cards */}
            {sortedSuppliers.map((supplier) => (
              <div
                key={supplier.supplier_id}
                className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow bg-white"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-brand-600" />
                        <h3 className="text-lg font-bold text-gray-900">
                          {supplier.supplier_id}
                        </h3>
                      </div>
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          supplier.status === 'Active'
                            ? 'bg-green-100 text-green-700'
                            : supplier.status === 'Inactive'
                            ? 'bg-gray-100 text-gray-700'
                            : supplier.status === 'Pending'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {supplier.status || 'N/A'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {supplier.company_name && (
                        <div className="flex items-start gap-2 text-sm">
                          <Building2 className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Company:</span>
                            <span className="ml-2 text-gray-900 font-semibold">{supplier.company_name}</span>
                          </div>
                        </div>
                      )}

                      {supplier.contact_name && (
                        <div className="flex items-start gap-2 text-sm">
                          <User className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Contact:</span>
                            <span className="ml-2 text-gray-900 font-semibold">{supplier.contact_name}</span>
                          </div>
                        </div>
                      )}

                      {supplier.contact_email && (
                        <div className="flex items-start gap-2 text-sm">
                          <Mail className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Email:</span>
                            <a href={`mailto:${supplier.contact_email}`} className="ml-2 text-brand-600 hover:text-brand-700 font-medium">
                              {supplier.contact_email}
                            </a>
                          </div>
                        </div>
                      )}

                      {supplier.contact_phone && (
                        <div className="flex items-start gap-2 text-sm">
                          <Phone className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Phone:</span>
                            <a href={`tel:${supplier.contact_phone}`} className="ml-2 text-brand-600 hover:text-brand-700 font-medium">
                              {supplier.contact_phone}
                            </a>
                          </div>
                        </div>
                      )}

                      {supplier.address && (
                        <div className="flex items-start gap-2 text-sm">
                          <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Address:</span>
                            <span className="ml-2 text-gray-900">{supplier.address}</span>
                          </div>
                        </div>
                      )}

                      {supplier.products && (
                        <div className="flex items-start gap-2 text-sm">
                          <Package className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Products:</span>
                            <span className="ml-2 text-gray-900">{supplier.products}</span>
                          </div>
                        </div>
                      )}

                      {supplier.last_interaction && (
                        <div className="flex items-start gap-2 text-sm">
                          <Calendar className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-gray-500 font-medium">Last Interaction:</span>
                            <span className="ml-2 text-gray-900 font-medium">{formatDate(supplier.last_interaction)}</span>
                          </div>
                        </div>
                      )}
                    </div>

                    {supplier.capacity && (
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Capacity:</span> {supplier.capacity}
                      </div>
                    )}

                    {supplier.certifications && (
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Certifications:</span> {supplier.certifications}
                      </div>
                    )}

                    {supplier.contract_value && (
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Contract Value:</span> {supplier.contract_value}
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => toggleSupplier(supplier.supplier_id)}
                    className="ml-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Toggle details"
                  >
                    {expandedSuppliers[supplier.supplier_id] ? (
                      <ChevronUp className="w-5 h-5" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </button>
                </div>

                {expandedSuppliers[supplier.supplier_id] && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="space-y-3">
                      {supplier.website && (
                        <div className="text-sm">
                          <span className="text-gray-500 font-medium">Website:</span>
                          <a
                            href={supplier.website.startsWith('http') ? supplier.website : `https://${supplier.website}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 text-brand-600 hover:text-brand-700 font-medium"
                          >
                            {supplier.website}
                          </a>
                        </div>
                      )}

                      {supplier.notes && (
                        <div className="text-sm">
                          <span className="text-gray-500 font-medium">Notes:</span>
                          <p className="mt-1 text-gray-700 whitespace-pre-wrap">{supplier.notes}</p>
                        </div>
                      )}

                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs font-semibold text-gray-500 mb-2">Full Details (JSON):</p>
                        <pre className="text-xs overflow-auto font-mono">
                          {JSON.stringify(supplier, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AllSuppliers;

