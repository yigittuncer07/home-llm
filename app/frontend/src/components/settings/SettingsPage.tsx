import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { getUserConfig, updateUserConfig } from '../../api/userConfig';

export default function SettingsPage() {
  const [prompt, setPrompt] = useState('');
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getUserConfig()
      .then(({ personalized_prompt }) => {
        setPrompt(personalized_prompt);
        setOriginalPrompt(personalized_prompt);
      })
      .catch(() => toast.error('Failed to load settings.'))
      .finally(() => setIsLoading(false));
  }, []);

  async function handleSave() {
    setIsSaving(true);
    try {
      const updated = await updateUserConfig({ personalized_prompt: prompt });
      setOriginalPrompt(updated.personalized_prompt);
      toast.success('Settings saved.');
    } catch {
      toast.error('Failed to save settings.');
    } finally {
      setIsSaving(false);
    }
  }

  const isDirty = prompt !== originalPrompt;

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950 p-6 md:p-10">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Settings</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
          Customize your AI assistant's behavior.
        </p>

        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
          <label
            htmlFor="personalized-prompt"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Personalized system prompt
          </label>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
            This instruction is appended to the system prompt for every message you send.
          </p>

          {isLoading ? (
            <div className="h-32 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
          ) : (
            <textarea
              id="personalized-prompt"
              rows={6}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Always respond in a concise, technical style. Prefer code examples over long explanations."
              className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 px-3 py-2 resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          )}

          <div className="mt-4 flex items-center justify-end gap-3">
            {isDirty && (
              <button
                onClick={() => setPrompt(originalPrompt)}
                className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                Discard
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={!isDirty || isSaving || isLoading}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {isSaving ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
