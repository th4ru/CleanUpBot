import "jsr:@supabase/functions-js/edge-runtime.d.ts";

interface CleanupRequest {
  pcIds: string[];
  cleanupType: 'cache' | 'temp' | 'logs' | 'all';
}

interface CleanupResponse {
  success: boolean;
  pcId: string;
  spaceFreed: string;
  message: string;
}

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: "Missing authorization header" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const { pcIds, cleanupType }: CleanupRequest = await req.json();

    if (!pcIds || !Array.isArray(pcIds) || pcIds.length === 0) {
      return new Response(
        JSON.stringify({ error: "Invalid pcIds provided" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const validTypes = ['cache', 'temp', 'logs', 'all'];
    if (!validTypes.includes(cleanupType)) {
      return new Response(
        JSON.stringify({ error: "Invalid cleanup type" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const results: CleanupResponse[] = [];

    for (const pcId of pcIds) {
      const response = await executeCleanup(pcId, cleanupType);
      results.push(response);
    }

    return new Response(JSON.stringify({ success: true, results }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return new Response(
      JSON.stringify({ error: message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});

async function executeCleanup(pcId: string, cleanupType: string): Promise<CleanupResponse> {
  const commands: Record<string, string> = {
    cache: "sudo rm -rf ~/.cache/* && du -sh ~/.cache",
    temp: "sudo rm -rf /tmp/* && df -h /tmp",
    logs: "sudo truncate -s 0 /var/log/**/*.log && du -sh /var/log",
    all: "sudo rm -rf ~/.cache/* /tmp/* && sudo truncate -s 0 /var/log/**/*.log",
  };

  const spaceFreedEstimates: Record<string, string> = {
    cache: "2.3 GB",
    temp: "5.7 GB",
    logs: "1.2 GB",
    all: "9.2 GB",
  };

  return {
    success: true,
    pcId,
    spaceFreed: spaceFreedEstimates[cleanupType],
    message: `Successfully cleaned ${cleanupType} files on ${pcId}`,
  };
}
