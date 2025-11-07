import { useState } from 'react';
import { Save, Search, Loader2, CheckCircle, AlertCircle, ChevronDown, Database, Building2, User, Mail, Phone, MapPin, Package, CreditCard, Globe, FileText, Hash, Calendar } from 'lucide-react';
import { supplierApi } from '../services/api';

function AddSupplierProfile() {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [formData, setFormData] = useState({
    // Card 1: Company Information
    vendor_legal_name: '',
    vendor_type: '',
    business_category: '',
    country_of_incorporation: '',
    website_url: '',
    
    // Card 2: Identifiers
    tax_id: '',
    amazon_vendor_code: '',
    business_type: '',
    
    // Card 3: Primary Contact
    contact_full_name: '',
    contact_role_dept: '',
    contact_email: '',
    contact_phone: '',
    timezone: '',
    preferred_language: '',
    
    // Card 4: Business Address
    registered_address: '',
    billing_address: '',
    
    // Card 5: Product Details
    brand_name: '',
    product_name_title: '',
    product_category: '',
    product_subcategory: '',
    pack_size: '',
    unit_cost: '',
    retail_cost: '',
    product_notes: '',
    
    // Card 6: Payment Details
    currency: '',
    payment_method: '',
    beneficiary_name: '',
    bank_name: '',
    routing_no: '',
    account_no: '',
    
    // Card 7: Status
    vendor_status: 'Active',
    created_on: '',
    last_updated_on: '',
    
    // Legacy fields for backward compatibility
    supplier_id: '',
    company_name: '',
    contact_name: '',
    address: '',
    products: '',
    capacity: '',
    certifications: '',
    website: '',
    status: 'Active',
    contract_value: '',
    last_interaction: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [expandedSuppliers, setExpandedSuppliers] = useState({});

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setSearchResults(null);
      return;
    }

    setSearching(true);
    try {
      const response = await supplierApi.listSuppliers(searchTerm);
      setSearchResults(response);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error searching suppliers');
    } finally {
      setSearching(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleLoadProfile = async (supplierId) => {
    try {
      const response = await supplierApi.getSupplierProfile(supplierId);
      if (response.status === 'success' && response.data) {
        const profile = response.data;
        setFormData({
          supplier_id: profile.supplier_id || '',
          company_name: profile.company_name || '',
          contact_name: profile.contact_name || '',
          contact_email: profile.contact_email || '',
          contact_phone: profile.contact_phone || '',
          address: profile.address || '',
          products: profile.products || '',
          capacity: profile.capacity || '',
          certifications: profile.certifications || '',
          website: profile.website || '',
          status: profile.status || 'Active',
          contract_value: profile.contract_value || '',
          last_interaction: profile.last_interaction ? profile.last_interaction.split('T')[0] : '',
          notes: profile.notes || '',
        });
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No existing profile found for this supplier ID');
      } else {
        setError(err.response?.data?.detail || err.message || 'Error loading profile');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.amazon_vendor_code.trim() && !formData.vendor_legal_name.trim()) {
      setError('Please enter Amazon Vendor Code or Vendor Legal Name');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Map new fields to legacy fields for backend compatibility
      const profileData = {
        supplier_id: formData.amazon_vendor_code || formData.vendor_legal_name.replace(/\s+/g, '-').toUpperCase(),
        company_name: formData.vendor_legal_name,
        contact_name: formData.contact_full_name,
        contact_email: formData.contact_email,
        contact_phone: formData.contact_phone,
        address: formData.registered_address || formData.billing_address,
        products: `${formData.product_category}${formData.product_subcategory ? ' - ' + formData.product_subcategory : ''}`,
        capacity: formData.pack_size,
        certifications: formData.business_category,
        website: formData.website_url,
        status: formData.vendor_status,
        contract_value: formData.retail_cost,
        last_interaction: formData.last_updated_on ? new Date(formData.last_updated_on).toISOString() : null,
        notes: formData.product_notes,
        // Include all new fields
        ...formData,
      };

      // Remove null/empty values
      Object.keys(profileData).forEach(key => {
        if (profileData[key] === '' || profileData[key] === null) {
          delete profileData[key];
        }
      });

      const response = await supplierApi.addSupplierProfile(profileData);
      setResult(response);
      // Clear form on success - reset to initial state
      setFormData({
        vendor_legal_name: '',
        vendor_type: '',
        business_category: '',
        country_of_incorporation: '',
        website_url: '',
        tax_id: '',
        amazon_vendor_code: '',
        business_type: '',
        contact_full_name: '',
        contact_role_dept: '',
        contact_email: '',
        contact_phone: '',
        timezone: '',
        preferred_language: '',
        registered_address: '',
        billing_address: '',
        brand_name: '',
        product_name_title: '',
        product_category: '',
        product_subcategory: '',
        pack_size: '',
        unit_cost: '',
        retail_cost: '',
        product_notes: '',
        currency: '',
        payment_method: '',
        beneficiary_name: '',
        bank_name: '',
        routing_no: '',
        account_no: '',
        vendor_status: 'Active',
        created_on: '',
        last_updated_on: '',
        supplier_id: '',
        company_name: '',
        contact_name: '',
        address: '',
        products: '',
        capacity: '',
        certifications: '',
        website: '',
        status: 'Active',
        contract_value: '',
        last_interaction: '',
        notes: '',
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error saving supplier profile');
    } finally {
      setLoading(false);
    }
  };

  const toggleSupplier = (supplierId) => {
    setExpandedSuppliers((prev) => ({
      ...prev,
      [supplierId]: !prev[supplierId],
    }));
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="card-header">Add Supplier Profile (CRM)</h2>
        <p className="card-subtitle">
          Enter supplier profile information to store in the CRM database. This data will be
          automatically retrieved when querying suppliers.
        </p>

        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Search Existing Suppliers</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search by Supplier ID, Company Name, or Contact"
              className="input-field flex-1"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="btn-secondary flex items-center gap-2"
            >
              {searching ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Search
            </button>
          </div>

          {searchResults && (
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-3">
                Found {searchResults.count || 0} suppliers:
              </p>
              <div className="space-y-2">
                {(searchResults.data || []).slice(0, 10).map((supplier) => (
                  <div
                    key={supplier.supplier_id}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 shadow-sm transition-shadow"
                  >
                    <button
                      onClick={() => toggleSupplier(supplier.supplier_id)}
                      className="w-full flex items-center justify-between text-left"
                    >
                      <span className="font-medium text-gray-900">
                        {supplier.supplier_id} - {supplier.company_name || 'N/A'}
                      </span>
                      <ChevronDown
                        className={`w-4 h-4 text-gray-500 transition-transform ${
                          expandedSuppliers[supplier.supplier_id] ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                    {expandedSuppliers[supplier.supplier_id] && (
                      <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-auto">
                        {JSON.stringify(supplier, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 pt-8">
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Add/Update Supplier Profile</h3>
            <p className="text-gray-600 text-sm">Complete all sections to create a comprehensive supplier profile</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Card 1: Company Information */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Company Information</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">
                    Vendor Legal Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="vendor_legal_name"
                    value={formData.vendor_legal_name}
                    onChange={handleInputChange}
                    placeholder="Enter vendor legal name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Vendor Type</label>
                  <select
                    name="vendor_type"
                    value={formData.vendor_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  >
                    <option value="">Select vendor type</option>
                    <option value="Manufacturer">Manufacturer</option>
                    <option value="Brand Owner">Brand Owner</option>
                    <option value="Distributor">Distributor</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Business Category</label>
                  <select
                    name="business_category"
                    value={formData.business_category}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  >
                    <option value="">Select category</option>
                    <option value="Grocery">Grocery</option>
                    <option value="Apparel">Apparel</option>
                    <option value="Electronics">Electronics</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Country of Incorporation</label>
                  <input
                    type="text"
                    name="country_of_incorporation"
                    value={formData.country_of_incorporation}
                    onChange={handleInputChange}
                    placeholder="Enter country"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Website URL</label>
                  <input
                    type="url"
                    name="website_url"
                    value={formData.website_url}
                    onChange={handleInputChange}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
              </div>
              </div>
            </div>

            {/* Card 2: Identifiers */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-4 border-b border-indigo-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <Hash className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Identifiers</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Tax ID</label>
                  <input
                    type="text"
                    name="tax_id"
                    value={formData.tax_id}
                    onChange={handleInputChange}
                    placeholder="Enter tax ID"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Amazon Vendor Code</label>
                  <input
                    type="text"
                    name="amazon_vendor_code"
                    value={formData.amazon_vendor_code}
                    onChange={handleInputChange}
                    placeholder="Enter Amazon vendor code"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Business Type</label>
                  <select
                    name="business_type"
                    value={formData.business_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  >
                    <option value="">Select business type</option>
                    <option value="Corporation">Corporation</option>
                    <option value="LLC">LLC</option>
                    <option value="Partnership">Partnership</option>
                    <option value="Sole Proprietorship">Sole Proprietorship</option>
                  </select>
                </div>
              </div>
              </div>
            </div>

            {/* Card 3: Primary Contact */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-6 py-4 border-b border-emerald-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Primary Contact</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Full Name</label>
                  <input
                    type="text"
                    name="contact_full_name"
                    value={formData.contact_full_name}
                    onChange={handleInputChange}
                    placeholder="Enter full name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Role/Dept</label>
                  <input
                    type="text"
                    name="contact_role_dept"
                    value={formData.contact_role_dept}
                    onChange={handleInputChange}
                    placeholder="Enter role or department"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Email</label>
                  <input
                    type="email"
                    name="contact_email"
                    value={formData.contact_email}
                    onChange={handleInputChange}
                    placeholder="Enter email address"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Phone</label>
                  <input
                    type="tel"
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleInputChange}
                    placeholder="Enter phone number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">TimeZone</label>
                  <input
                    type="text"
                    name="timezone"
                    value={formData.timezone}
                    onChange={handleInputChange}
                    placeholder="e.g., UTC-5, EST"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Preferred Language</label>
                  <input
                    type="text"
                    name="preferred_language"
                    value={formData.preferred_language}
                    onChange={handleInputChange}
                    placeholder="e.g., English, Spanish"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
              </div>
              </div>
            </div>

            {/* Card 4: Business Address */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-amber-600 to-amber-700 px-6 py-4 border-b border-amber-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Business Address</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Registered Address</label>
                  <textarea
                    name="registered_address"
                    value={formData.registered_address}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Enter registered address"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900 resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Billing Address</label>
                  <textarea
                    name="billing_address"
                    value={formData.billing_address}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Enter billing address"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900 resize-none"
                  />
                </div>
              </div>
              </div>
            </div>

            {/* Card 5: Product Details */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 border-b border-purple-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <Package className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Product Details</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Brand Name</label>
                  <input
                    type="text"
                    name="brand_name"
                    value={formData.brand_name}
                    onChange={handleInputChange}
                    placeholder="Enter brand name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Product Name/Title</label>
                  <input
                    type="text"
                    name="product_name_title"
                    value={formData.product_name_title}
                    onChange={handleInputChange}
                    placeholder="Enter product name or title"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Product Category</label>
                  <input
                    type="text"
                    name="product_category"
                    value={formData.product_category}
                    onChange={handleInputChange}
                    placeholder="Enter product category"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Product Subcategory</label>
                  <input
                    type="text"
                    name="product_subcategory"
                    value={formData.product_subcategory}
                    onChange={handleInputChange}
                    placeholder="Enter product subcategory"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Pack Size</label>
                  <input
                    type="text"
                    name="pack_size"
                    value={formData.pack_size}
                    onChange={handleInputChange}
                    placeholder="Enter pack size"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Unit Cost</label>
                  <input
                    type="text"
                    name="unit_cost"
                    value={formData.unit_cost}
                    onChange={handleInputChange}
                    placeholder="Enter unit cost"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Retail Cost</label>
                  <input
                    type="text"
                    name="retail_cost"
                    value={formData.retail_cost}
                    onChange={handleInputChange}
                    placeholder="Enter retail cost"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Notes</label>
                  <textarea
                    name="product_notes"
                    value={formData.product_notes}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Enter product notes"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900 resize-none"
                  />
                </div>
              </div>
              </div>
            </div>

            {/* Card 6: Payment Details */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-rose-600 to-rose-700 px-6 py-4 border-b border-rose-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <CreditCard className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Payment Details</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Currency</label>
                  <input
                    type="text"
                    name="currency"
                    value={formData.currency}
                    onChange={handleInputChange}
                    placeholder="e.g., USD, EUR"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Payment Method</label>
                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  >
                    <option value="">Select payment method</option>
                    <option value="Wire Transfer">Wire Transfer</option>
                    <option value="ACH">ACH</option>
                    <option value="Check">Check</option>
                    <option value="Credit Card">Credit Card</option>
                    <option value="PayPal">PayPal</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Beneficiary Name</label>
                  <input
                    type="text"
                    name="beneficiary_name"
                    value={formData.beneficiary_name}
                    onChange={handleInputChange}
                    placeholder="Enter beneficiary name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Bank Name</label>
                  <input
                    type="text"
                    name="bank_name"
                    value={formData.bank_name}
                    onChange={handleInputChange}
                    placeholder="Enter bank name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Routing No</label>
                  <input
                    type="text"
                    name="routing_no"
                    value={formData.routing_no}
                    onChange={handleInputChange}
                    placeholder="Enter routing number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Account No</label>
                  <input
                    type="text"
                    name="account_no"
                    value={formData.account_no}
                    onChange={handleInputChange}
                    placeholder="Enter account number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
              </div>
              </div>
            </div>

            {/* Card 7: Status */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-teal-600 to-teal-700 px-6 py-4 border-b border-teal-600">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white">Status</h4>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Vendor Status</label>
                  <select
                    name="vendor_status"
                    value={formData.vendor_status}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                    <option value="Pending">Pending</option>
                    <option value="Suspended">Suspended</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Created On</label>
                  <input
                    type="date"
                    name="created_on"
                    value={formData.created_on}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2.5">Last Updated On</label>
                  <input
                    type="date"
                    name="last_updated_on"
                    value={formData.last_updated_on}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-gray-50 hover:bg-white text-gray-900"
                  />
                </div>
              </div>
              </div>
            </div>

            <div className="flex justify-end pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3.5 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-800 hover:to-slate-900 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Saving Profile...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    <span>Save Supplier Profile</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3 shadow-soft">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-6 p-5 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg flex items-start gap-3 shadow-soft">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-green-900 text-lg">
                  ✓ Supplier profile saved for {formData.supplier_id || result.data?.supplier_id}!
                </p>
                <p className="text-sm text-green-800 mt-1 font-medium">
                  This profile will be automatically retrieved when querying this supplier.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AddSupplierProfile;

