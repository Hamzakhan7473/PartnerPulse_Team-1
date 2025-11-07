import { useState } from 'react';
import { CheckCircle, AlertCircle, Loader2, Calendar } from 'lucide-react';
import { supplierApi } from '../services/api';

function AddSupplierData() {
  const [comments, setComments] = useState('');
  const [interactionDate, setInteractionDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!comments.trim()) {
      setError('Please enter comments about the supplier');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await supplierApi.ingestSupplierData(comments, interactionDate);
      setResult(response);
      setComments(''); // Clear form on success
      setInteractionDate(''); // Clear date on success
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error ingesting supplier data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-header">Add Supplier Information</h2>
      <p className="card-subtitle">
        Enter comments about the supplier. The system will automatically extract the supplier identifier
        and process the data into profile and episodic memory.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-semibold text-slate-800 mb-2.5">
              Interaction Date <span className="text-slate-500 font-normal">(optional)</span>
            </label>
            <div className="relative">
              <input
                type="date"
                value={interactionDate}
                onChange={(e) => setInteractionDate(e.target.value)}
                className="input-field bg-slate-50 hover:bg-white"
                max={new Date().toISOString().split('T')[0]}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
            </div>
            <p className="text-xs text-slate-500 mt-1.5">
              Select the date of interaction or when this information was recorded
            </p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-800 mb-2.5">
            Enter comments, reviews, or notes about the supplier:
          </label>
          <textarea
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Enter comments about the supplier. Include supplier identifier (ID, name, or company name). For example:

Supplier: SUP-001
Company: Acme Corp
Contact: John Doe, email: john@acme.com
Products: Electronics, Components

Recent interaction: Met with supplier on 2024-01-15. Discussed pricing for bulk orders. Very responsive company.
Quality: High quality products, on-time delivery
Capacity: Can handle orders up to 10,000 units/month"
            className="input-field resize-none bg-slate-50 hover:bg-white"
            rows={12}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing supplier data...
            </>
          ) : (
            'Submit Supplier Data'
          )}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3 shadow-soft">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-red-800 font-semibold">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-6 p-5 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg shadow-soft">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-bold text-green-900 mb-2 text-lg">
                ✓ Supplier data successfully processed!
              </p>
              <div className="text-sm text-green-800 space-y-2">
                <p className="font-semibold">
                  Supplier ID extracted: <span className="text-green-900 font-bold">{result.supplier_id || 'Unknown'}</span>
                </p>
                <div className="mt-3 pt-3 border-t border-green-200">
                  <p className="font-semibold mb-2">Processing Summary:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    <li>Supplier identifier extracted from comments</li>
                    <li>Comments stored in episodic memory</li>
                    <li>Profile information extracted and stored in profile memory</li>
                    <li>CRM data fetched and mapped</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AddSupplierData;

