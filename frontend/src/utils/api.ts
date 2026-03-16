const getSupabaseUrl = () => import.meta.env.VITE_SUPABASE_URL;
const getAnonKey = () => import.meta.env.VITE_SUPABASE_ANON_KEY;

export async function callCleanupFunction(pcIds: string[], cleanupType: 'cache' | 'temp' | 'logs' | 'all') {
  const apiUrl = `${getSupabaseUrl()}/functions/v1/cleanup`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAnonKey()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pcIds, cleanupType }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cleanup function error:', error);
    throw error;
  }
}

export async function callSystemStatusFunction() {
  const apiUrl = `${getSupabaseUrl()}/functions/v1/system-status`;

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAnonKey()}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('System status function error:', error);
    throw error;
  }
}
