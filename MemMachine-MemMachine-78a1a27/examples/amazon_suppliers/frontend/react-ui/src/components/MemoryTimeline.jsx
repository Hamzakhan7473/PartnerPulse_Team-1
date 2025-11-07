import { Fragment } from 'react';
import { Clock, Sparkles, Database, FileText } from 'lucide-react';

const EVENT_ICONS = {
  comments: Sparkles,
  profile_extraction: FileText,
  crm_profile: Database,
};

function buildMetaSummary(metadata = {}) {
  const parts = [];
  if (metadata.interaction_date) {
    parts.push(`Interaction: ${metadata.interaction_date}`);
  }
  if (metadata.data_type && !['comments', 'profile_extraction', 'crm_profile'].includes(metadata.data_type)) {
    parts.push(metadata.data_type.replace(/_/g, ' '));
  }
  if (metadata.source) {
    parts.push(`Source: ${metadata.source}`);
  }
  if (metadata.model) {
    parts.push(`Model: ${metadata.model}`);
  }
  return parts.join(' • ');
}

function formatTimestamp(timestamp) {
  if (!timestamp) {
    return 'Unknown date';
  }

  try {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return new Intl.DateTimeFormat('en', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch (err) {
    return timestamp;
  }
}

export default function MemoryTimeline({ events = [] }) {
  if (!events.length) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-soft p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Memory Timeline</h3>
            <p className="text-sm text-slate-500">No episodic events were returned for this supplier yet.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-soft p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
          <Clock className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-slate-800">Memory Timeline</h3>
          <p className="text-sm text-slate-500">Chronological view of episodic updates stored in MemMachine.</p>
        </div>
      </div>

      <div className="relative pl-6">
        <div className="absolute left-5 top-0 bottom-5 w-px bg-slate-200" aria-hidden="true" />

        <div className="space-y-8">
          {events.map((event, index) => {
            const Icon = EVENT_ICONS[event.type] || Sparkles;
            const timelineBadge = event.type?.replace(/_/g, ' ') || 'memory';
            const metaSummary = buildMetaSummary(event.metadata);

            return (
              <Fragment key={`${event.timestamp}-${index}`}>
                <div className="relative pl-6">
                  <span className="absolute -left-[1.4rem] top-1.5 inline-flex items-center justify-center w-8 h-8 rounded-full border border-slate-200 bg-white shadow-sm">
                    <Icon className="w-4 h-4 text-slate-500" aria-hidden="true" />
                    <span className="sr-only">{timelineBadge}</span>
                  </span>

                  <div className="flex flex-col gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
                        {timelineBadge}
                      </span>
                      <span className="text-xs text-slate-400">
                        {formatTimestamp(event.timestamp) || 'Unknown date'}
                      </span>
                    </div>

                    <p className="text-sm text-slate-700 whitespace-pre-line leading-relaxed">
                      {event.summary || event.content || 'No content available'}
                    </p>

                    {(metaSummary || event.score !== undefined) && (
                      <div className="text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                    {metaSummary && <p>{metaSummary}</p>}
                    {event.score !== undefined && event.score !== null && !Number.isNaN(Number(event.score)) && (
                      <p>
                        Similarity score: {
                          (() => {
                            const rawScore = Number(event.score);
                            const percent = rawScore > 1 ? rawScore : rawScore * 100;
                            return `${percent.toFixed(1)}%`;
                          })()
                        }
                      </p>
                    )}
                      </div>
                    )}
                  </div>
                </div>

                {index < events.length - 1 && <div className="h-px bg-slate-100 ml-6" />}
              </Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}

