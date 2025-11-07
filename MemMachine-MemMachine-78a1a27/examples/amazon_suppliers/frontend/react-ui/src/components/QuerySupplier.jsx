import { useState } from 'react';
import { Send, Loader2, AlertCircle, ChevronDown, ChevronUp, FileText, Lightbulb, User, Clock, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { supplierApi } from '../services/api';
import MemoryTimeline from './MemoryTimeline';
import SystemStatus from './SystemStatus';

function QuerySupplier({ modelId, queryHistory, setQueryHistory }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [showRawData, setShowRawData] = useState(false);
  const [showEpisodicMemory, setShowEpisodicMemory] = useState(false);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const quickPrompts = [
    'Summarize the latest updates for supplier SUP-001 and highlight risks.',
    'What strategic follow-ups should we schedule for TechGlobal Electronics?',
    'Compare the delivery performance of our top suppliers over the last quarter.',
    'Remind me of any outstanding issues or escalations for Premium Apparel Co.',
    'Give me key profile facts about supplier SUP-005 before my call.',
  ];

  const buildTimelineEvents = (contextData) => {
    if (!contextData) {
      return [];
    }

    const events = [];

    const ingestEpisode = (episode) => {
      if (!episode || typeof episode !== 'object') {
        return;
      }

      const metadata = episode.metadata || episode.user_metadata || {};
      const baseContent = episode.summary || episode.content || episode.episode_content || episode.text || '';
      const timestamp = episode.timestamp || metadata.timestamp || metadata.created_at || metadata.interaction_date || null;
      const score = typeof episode.score === 'number' ? episode.score : typeof episode.similarity === 'number' ? episode.similarity : undefined;
      const type = metadata.data_type || episode.episode_type || episode.type || undefined;

      events.push({
        timestamp,
        content: baseContent,
        summary: baseContent,
        metadata,
        score,
        type,
      });
    };

    const iterate = (value) => {
      if (!value) return;
      if (Array.isArray(value)) {
        value.forEach(iterate);
        return;
      }
      ingestEpisode(value);
    };

    iterate(contextData);

    return events
      .filter((event) => event.content)
      .sort((a, b) => {
        const aTime = a.timestamp ? new Date(a.timestamp).getTime() : 0;
        const bTime = b.timestamp ? new Date(b.timestamp).getTime() : 0;
        return bTime - aTime;
      });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a query about the supplier');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);
    setTimelineEvents([]);

    try {
      // Step 1: Query supplier to get memory data
      let queryResult;
      try {
        queryResult = await supplierApi.querySupplier(query);
      } catch (queryErr) {
        throw new Error(`Failed to query supplier: ${queryErr.response?.data?.detail || queryErr.message}`);
      }

      const supplierId = queryResult.supplier_id || 'Unknown';
      const formattedQuery = queryResult.formatted_query;

      if (!formattedQuery) {
        throw new Error('No formatted query available from the backend');
      }

      // Step 2: Call LLM chat endpoint
      const messages = [{ role: 'user', content: formattedQuery }];
      let chatResult;
      try {
        chatResult = await supplierApi.chatWithLLM(messages, supplierId, modelId);
      } catch (chatErr) {
        // If chat fails, check if it's a 404 or other error
        if (chatErr.response?.status === 404) {
          throw new Error('LLM chat endpoint not found. Please ensure the backend server is running with the latest code.');
        }
        if (chatErr.response?.status === 401 || chatErr.response?.status === 500) {
          const errorDetail = chatErr.response?.data?.detail || chatErr.message;
          throw new Error(`LLM API error: ${errorDetail}. Please check your API key configuration.`);
        }
        // For other errors, show the query result anyway with a warning
        setResponse({
          supplierId,
          queryResult,
          llmResponse: `⚠️ Error generating LLM response: ${chatErr.response?.data?.detail || chatErr.message}\n\nSupplier information retrieved successfully. Please check the raw data below or configure your API key.`,
          metadata: null,
        });
        // Don't throw - show the response we created above
        return;
      }

      const episodicContext = queryResult?.data?.context;
      setTimelineEvents(buildTimelineEvents(episodicContext));

      setResponse({
        supplierId,
        queryResult,
        llmResponse: chatResult.response,
        metadata: chatResult.metadata,
      });
      
      // Debug logging
      console.log('QuerySupplier - Response set:', {
        supplierId,
        hasCrmProfile: !!queryResult?.data?.crm_profile,
        crmProfileKeys: queryResult?.data?.crm_profile ? Object.keys(queryResult.data.crm_profile) : [],
        crmCompanyName: queryResult?.data?.crm_profile?.company_name,
      });

      // Add to history
      setQueryHistory([
        ...queryHistory,
        {
          supplier_id: supplierId,
          query,
          response: chatResult.response,
        },
      ]);

      setQuery(''); // Clear input on success
    } catch (err) {
      console.error('Query error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Error querying supplier';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Format CRM data for display
  const formatCrmData = (crmData) => {
    if (!crmData) return null;
    
    const fields = [];
    if (crmData.company_name) fields.push(`• Company Name: ${crmData.company_name}`);
    if (crmData.contact_name) fields.push(`• Contact Person: ${crmData.contact_name}`);
    if (crmData.contact_email) fields.push(`• Email: ${crmData.contact_email}`);
    if (crmData.contact_phone) fields.push(`• Phone: ${crmData.contact_phone}`);
    if (crmData.address) fields.push(`• Address: ${crmData.address}`);
    if (crmData.website) fields.push(`• Website: ${crmData.website}`);
    if (crmData.products) fields.push(`• Products/Services: ${crmData.products}`);
    if (crmData.capacity) fields.push(`• Capacity: ${crmData.capacity}`);
    if (crmData.certifications) fields.push(`• Certifications: ${crmData.certifications}`);
    if (crmData.supplier_id) fields.push(`• CRM ID (Supplier ID): ${crmData.supplier_id}`);
    if (crmData.status) fields.push(`• Account Status: ${crmData.status}`);
    if (crmData.contract_value) fields.push(`• Contract Value: ${crmData.contract_value}`);
    if (crmData.last_interaction) fields.push(`• Last Interaction: ${crmData.last_interaction}`);
    if (crmData.notes) fields.push(`• Notes: ${crmData.notes}`);
    
    return fields.length > 0 ? fields.join('\n') : null;
  };

  // Parse LLM response into sections
  const parseResponseSections = (responseText, responseObj = null) => {
    const sections = {
      summary: '',
      strategicSuggestions: '',
      profileInformation: '',
      episodicMemory: '',
    };

    // Method 1: Try markdown headers with ## or ###
    let summaryMatch = responseText.match(/(?:##|###)\s*Summary\s*\n\n(.*?)(?=(?:##|###)\s|$)/is);
    let strategicMatch = responseText.match(/(?:##|###)\s*Strategic\s+Suggestions\s*\n\n(.*?)(?=(?:##|###)\s|$)/is);
    let profileMatch = responseText.match(/(?:##|###)\s*Profile\s+Information\s*\n\n(.*?)(?=(?:##|###)\s|$)/is);
    let episodicMatch = responseText.match(/(?:##|###)\s*Episodic\s+Memory\s+Summary\s*\n\n(.*?)(?=(?:##|###)\s|$)/is);

    if (summaryMatch) sections.summary = summaryMatch[1].trim();
    if (strategicMatch) sections.strategicSuggestions = strategicMatch[1].trim();
    if (profileMatch) sections.profileInformation = profileMatch[1].trim();
    if (episodicMatch) sections.episodicMemory = episodicMatch[1].trim();

    // Method 2: Try numbered sections with bold markers (1. **Summary** or 1. **Summary**:)
    if (!sections.summary) {
      summaryMatch = responseText.match(/1\.\s*\*\*Summary\*\*[:\s]*\n\n(.*?)(?=2\.\s*\*\*|##|###|$)/is);
      if (summaryMatch) sections.summary = summaryMatch[1].trim();
    }
    if (!sections.strategicSuggestions) {
      strategicMatch = responseText.match(/2\.\s*\*\*Strategic\s+Suggestions\*\*[:\s]*\n\n(.*?)(?=3\.\s*\*\*|##|###|$)/is);
      if (strategicMatch) sections.strategicSuggestions = strategicMatch[1].trim();
    }
    if (!sections.profileInformation) {
      profileMatch = responseText.match(/3\.\s*\*\*Profile\s+Information\*\*[:\s]*\n\n(.*?)(?=4\.\s*\*\*|##|###|$)/is);
      if (profileMatch) sections.profileInformation = profileMatch[1].trim();
    }
    if (!sections.episodicMemory) {
      episodicMatch = responseText.match(/4\.\s*\*\*Episodic\s+Memory\s+Summary\*\*[:\s]*\n\n(.*?)(?=$)/is);
      if (episodicMatch) sections.episodicMemory = episodicMatch[1].trim();
    }

    // Method 3: Try without bold markers (1. Summary)
    if (!sections.summary) {
      summaryMatch = responseText.match(/1\.\s*Summary[:\s]*\n\n(.*?)(?=2\.\s*Strategic|##|###|$)/is);
      if (summaryMatch) sections.summary = summaryMatch[1].trim();
    }
    if (!sections.strategicSuggestions) {
      strategicMatch = responseText.match(/2\.\s*Strategic\s+Suggestions[:\s]*\n\n(.*?)(?=3\.\s*Profile|##|###|$)/is);
      if (strategicMatch) sections.strategicSuggestions = strategicMatch[1].trim();
    }
    if (!sections.profileInformation) {
      profileMatch = responseText.match(/3\.\s*Profile\s+Information[:\s]*\n\n(.*?)(?=4\.\s*Episodic|##|###|$)/is);
      if (profileMatch) sections.profileInformation = profileMatch[1].trim();
    }
    if (!sections.episodicMemory) {
      episodicMatch = responseText.match(/4\.\s*Episodic\s+Memory\s+Summary[:\s]*\n\n(.*?)(?=$)/is);
      if (episodicMatch) sections.episodicMemory = episodicMatch[1].trim();
    }

    // Method 4: Try splitting by bold headers in the text itself
    if (!sections.summary) {
      summaryMatch = responseText.match(/\*\*Summary\*\*[:\s]*\n\n(.*?)(?=\*\*Strategic|##|###|$)/is);
      if (summaryMatch) sections.summary = summaryMatch[1].trim();
    }
    if (!sections.strategicSuggestions) {
      strategicMatch = responseText.match(/\*\*Strategic\s+Suggestions\*\*[:\s]*\n\n(.*?)(?=\*\*Profile|##|###|$)/is);
      if (strategicMatch) sections.strategicSuggestions = strategicMatch[1].trim();
    }
    if (!sections.profileInformation) {
      profileMatch = responseText.match(/\*\*Profile\s+Information\*\*[:\s]*\n\n(.*?)(?=\*\*Episodic|##|###|$)/is);
      if (profileMatch) sections.profileInformation = profileMatch[1].trim();
    }
    if (!sections.episodicMemory) {
      episodicMatch = responseText.match(/\*\*Episodic\s+Memory\s+Summary\*\*[:\s]*\n\n(.*?)(?=$)/is);
      if (episodicMatch) sections.episodicMemory = episodicMatch[1].trim();
    }

    // Method 5: Try to find sections by looking for common patterns (case-insensitive)
    // Split by "Strategic Suggestions" heading
    const strategicIndex = responseText.search(/(?:Strategic\s+Suggestions|##\s*Strategic)/i);
    const profileIndex = responseText.search(/(?:Profile\s+Information|##\s*Profile)/i);
    const episodicIndex = responseText.search(/(?:Episodic\s+Memory\s+Summary|Episodic\s+Memory|##\s*Episodic)/i);

    // Extract summary (everything before Strategic Suggestions or first section)
    if (!sections.summary) {
      let summaryEnd = strategicIndex;
      if (summaryEnd < 0) summaryEnd = profileIndex;
      if (summaryEnd < 0) summaryEnd = responseText.length;
      
      if (summaryEnd > 0) {
        const summaryText = responseText.substring(0, summaryEnd);
        // Remove any title/header from start like "Supplier: SUP-002"
        const cleanSummary = summaryText
          .replace(/^.*?Supplier[^]*?[:/]/is, '')
          .replace(/^.*?\*\*Summary\*\*[:\s]*/is, '')
          .replace(/^.*?Summary[:\s]*/is, '')
          .trim();
        if (cleanSummary.length > 10) {
          sections.summary = cleanSummary;
        }
      }
    }

    // Extract strategic suggestions
    if (!sections.strategicSuggestions && strategicIndex >= 0) {
      const endIndex = profileIndex > strategicIndex ? profileIndex : (episodicIndex > strategicIndex ? episodicIndex : responseText.length);
      const strategicText = responseText.substring(strategicIndex, endIndex);
      const cleanStrategic = strategicText
        .replace(/.*?Strategic\s+Suggestions[:\s]*/is, '')
        .replace(/.*?\*\*Strategic\s+Suggestions\*\*[:\s]*/is, '')
        .trim();
      if (cleanStrategic.length > 10) {
        sections.strategicSuggestions = cleanStrategic;
      }
    }

    // Extract profile information
    if (!sections.profileInformation && profileIndex >= 0) {
      const endIndex = episodicIndex > profileIndex ? episodicIndex : responseText.length;
      const profileText = responseText.substring(profileIndex, endIndex);
      const cleanProfile = profileText
        .replace(/.*?Profile\s+Information[:\s]*/is, '')
        .replace(/.*?\*\*Profile\s+Information\*\*[:\s]*/is, '')
        .trim();
      if (cleanProfile.length > 10) {
        sections.profileInformation = cleanProfile;
      }
    }

    // Extract episodic memory
    if (!sections.episodicMemory && episodicIndex >= 0) {
      const episodicText = responseText.substring(episodicIndex);
      const cleanEpisodic = episodicText
        .replace(/.*?Episodic\s+Memory[^]*?Summary[:\s]*/is, '')
        .replace(/.*?Episodic\s+Memory[:\s]*/is, '')
        .trim();
      if (cleanEpisodic.length > 10) {
        sections.episodicMemory = cleanEpisodic;
      }
    }

    // Fallback: If no structured sections found, try to manually parse
    const hasSections = sections.summary || sections.strategicSuggestions || sections.profileInformation || sections.episodicMemory;
    if (!hasSections) {
      // Last resort: try to split by common section markers
      const parts = responseText.split(/(?:Strategic\s+Suggestions|Profile\s+Information|Episodic\s+Memory)/i);
      if (parts.length > 1) {
        // First part is likely summary
        sections.summary = parts[0].replace(/^.*?Summary[:\s]*/is, '').trim();
        // Try to extract other sections from remaining parts
        for (let i = 1; i < parts.length; i++) {
          const part = parts[i];
          if (part.toLowerCase().includes('strategic') && !sections.strategicSuggestions) {
            sections.strategicSuggestions = part.replace(/.*?Suggestions[:\s]*/is, '').trim();
          } else if (part.toLowerCase().includes('profile') && !sections.profileInformation) {
            sections.profileInformation = part.replace(/.*?Information[:\s]*/is, '').trim();
          } else if (part.toLowerCase().includes('episodic') && !sections.episodicMemory) {
            sections.episodicMemory = part.replace(/.*?Summary[:\s]*/is, '').trim();
          }
        }
      }
    }

    // Final check: if we still don't have sections, display as-is but still try to show cards
    const finalHasSections = sections.summary || sections.strategicSuggestions || sections.profileInformation || sections.episodicMemory;
    if (!finalHasSections) {
      // Display as single card but with better formatting
      return (
        <div className="card">
          <div className="prose prose-sm max-w-none prose-headings:font-bold prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-li:text-gray-700">
            <ReactMarkdown>{responseText}</ReactMarkdown>
          </div>
        </div>
      );
    }

    // Always show cards, even if some sections are empty
    // This ensures the UI structure is consistent
    return (
      <>
        {/* Summary Card */}
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 border-b border-blue-600">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Summary</h3>
            </div>
          </div>
          <div className="p-6">
            {sections.summary ? (
              <div className="prose prose-sm max-w-none prose-p:text-slate-700 prose-strong:text-slate-900">
                <ReactMarkdown>{sections.summary}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-slate-500 italic">No summary available</p>
            )}
          </div>
        </div>

        {/* Strategic Suggestions Card */}
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="bg-gradient-to-r from-yellow-600 to-yellow-700 px-6 py-4 border-b border-yellow-600">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Strategic Suggestions</h3>
            </div>
          </div>
          <div className="p-6">
            {sections.strategicSuggestions ? (
              <div className="prose prose-sm max-w-none prose-p:text-slate-700 prose-ul:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                <ReactMarkdown>{sections.strategicSuggestions}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-slate-500 italic">No strategic suggestions available</p>
            )}
          </div>
        </div>

        {/* Profile Information Card */}
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 border-b border-green-600">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Profile Information</h3>
            </div>
          </div>
          <div className="p-6">
            {(() => {
              // Check if LLM provided valid profile information (prioritize LLM format)
              const hasValidLlmProfile = sections.profileInformation && 
                sections.profileInformation.trim() !== '' && 
                !sections.profileInformation.toLowerCase().includes('(none available)') && 
                !sections.profileInformation.toLowerCase().includes('(na)') &&
                !sections.profileInformation.toLowerCase().includes('no profile memory');
              
              // If LLM provided valid profile information, use it (this is the preferred format)
              if (hasValidLlmProfile) {
                return (
                  <div className="prose prose-sm max-w-none prose-p:text-slate-700 prose-ul:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                    <ReactMarkdown>{sections.profileInformation}</ReactMarkdown>
                  </div>
                );
              }
              
              // Fallback to CRM data only if LLM didn't provide valid profile information
              const crmData = responseObj?.queryResult?.data?.crm_profile;
              const hasCrmData = crmData && Object.keys(crmData).length > 0;
              
              if (hasCrmData) {
                const formattedCrm = formatCrmData(crmData);
                if (formattedCrm) {
                  return (
                    <div className="prose prose-sm max-w-none prose-p:text-slate-700 prose-ul:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                      <ReactMarkdown>{formattedCrm}</ReactMarkdown>
                    </div>
                  );
                }
              }
              
              // No data available
              return <p className="text-slate-500 italic">No profile information available</p>;
            })()}
          </div>
        </div>

        {/* Episodic Memory Card (Collapsible) */}
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 border-b border-purple-600">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Episodic Memory Summary</h3>
            </div>
          </div>
          <div className="p-6">
            {sections.episodicMemory ? (
              <>
                <button
                  onClick={() => setShowEpisodicMemory(!showEpisodicMemory)}
                  className="flex items-center gap-2 text-sm font-semibold text-slate-700 hover:text-slate-900 transition-colors w-full text-left mb-4"
                >
                  {showEpisodicMemory ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Hide Episodic Memory
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      Show Episodic Memory
                    </>
                  )}
                </button>
                {showEpisodicMemory && (
                  <div className="prose prose-sm max-w-none prose-p:text-slate-700 prose-ul:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                    <ReactMarkdown>{sections.episodicMemory}</ReactMarkdown>
                  </div>
                )}
              </>
            ) : (
              <p className="text-slate-500 italic">No episodic memory available</p>
            )}
          </div>
        </div>
      </>
    );
  };

  const structuredResponse = response ? parseResponseSections(response.llmResponse || '', response) : null;

  const handleQuickPrompt = (prompt) => {
    setQuery(prompt);
  };

  return (
    <div className="space-y-6">
      <SystemStatus />

      <div className="card">
        <h2 className="card-header">Query Supplier Information</h2>
        <p className="card-subtitle">
          Enter your query about a supplier. The system will automatically identify the supplier from your query.
        </p>

        <div className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 mb-4">
          <div className="flex items-start gap-3">
            <div className="mt-1">
              <Sparkles className="w-4 h-4 text-slate-500" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-slate-700">Try a quick prompt</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {quickPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => handleQuickPrompt(prompt)}
                    className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 hover:border-slate-400 transition-colors"
                  >
                    <Sparkles className="w-4 h-4 text-slate-500" />
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
                  <label className="block text-sm font-semibold text-slate-800 mb-2.5">
              Enter your query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tell me everything about supplier SUP-001
or
What's the status of Acme Corp?
or
Tell me about the supplier we discussed last week"
                    className="input-field resize-none bg-slate-50 hover:bg-white"
              rows={6}
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
                Querying supplier information...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Query Supplier
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3 shadow-soft">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
                    <p className="text-red-800 font-bold mb-1">Error</p>
                    <p className="text-red-700 text-sm font-medium">{error}</p>
              {error.includes('API key') && (
                <p className="text-red-600 text-xs mt-2">
                  💡 Tip: Make sure MODEL_API_KEY is set in your backend .env file
                </p>
              )}
              {error.includes('not found') && (
                <p className="text-red-600 text-xs mt-2">
                  💡 Tip: The backend server may need to be restarted to load the chat endpoint
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {response && (
        <div className="space-y-6">
          {response.metadata && (
            <div className="flex items-center justify-end gap-3 text-xs text-slate-600 bg-slate-100 px-4 py-2 rounded-lg font-medium">
              <span className="font-semibold">{response.metadata.model}</span>
              <span>•</span>
              <span>{response.metadata.latency.toFixed(2)}s</span>
              <span>•</span>
              <span>{response.metadata.tokens} tokens</span>
            </div>
          )}

          <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.8fr)_minmax(0,1fr)] gap-6 items-start">
            <div className="space-y-6">
              {structuredResponse}

              <div className="card">
                <button
                  onClick={() => setShowRawData(!showRawData)}
                  className="flex items-center gap-2 text-sm font-semibold text-slate-700 hover:text-slate-900 transition-colors"
                >
                  {showRawData ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Hide Raw Memory Data
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      Show Raw Memory Data
                    </>
                  )}
                </button>
                {showRawData && (
                  <pre className="mt-4 p-4 bg-gray-50 rounded-lg overflow-auto text-xs border border-gray-200 font-mono">
                    {JSON.stringify(response.queryResult, null, 2)}
                  </pre>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <MemoryTimeline events={timelineEvents} />
            </div>
          </div>
        </div>
      )}

      {queryHistory.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-5">Query History</h3>
          <div className="space-y-3">
            {queryHistory.slice(-5).reverse().map((entry, index) => (
              <details
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors shadow-sm"
              >
                <summary className="font-semibold text-gray-900 cursor-pointer flex items-center justify-between">
                  <span>Query {queryHistory.length - index}: {entry.supplier_id}</span>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </summary>
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-3 text-sm">
                  <p className="font-semibold text-gray-700">
                    <span className="text-gray-500">Query:</span> {entry.query}
                  </p>
                  <div className="prose prose-sm max-w-none prose-headings:font-bold prose-p:text-gray-700">
                    <ReactMarkdown>{entry.response}</ReactMarkdown>
                  </div>
                </div>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default QuerySupplier;

