import "jsr:@supabase/functions-js/edge-runtime.d.ts";

interface SystemStatusResponse {
  pcId: string;
  pcName: string;
  status: 'online' | 'offline';
  uptime: string;
  cpu: number;
  memory: number;
  lastSeen: string;
  ipAddress: string;
}

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
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

    const systems: SystemStatusResponse[] = [
      {
        pcId: '1',
        pcName: 'LAB-PC-001',
        status: 'online',
        uptime: '5d 12h 34m',
        cpu: 45,
        memory: 62,
        lastSeen: 'Active now',
        ipAddress: '192.168.1.101',
      },
      {
        pcId: '2',
        pcName: 'LAB-PC-002',
        status: 'online',
        uptime: '3d 8h 15m',
        cpu: 78,
        memory: 84,
        lastSeen: 'Active now',
        ipAddress: '192.168.1.102',
      },
      {
        pcId: '3',
        pcName: 'LAB-PC-003',
        status: 'offline',
        uptime: '0d 0h 0m',
        cpu: 0,
        memory: 0,
        lastSeen: '2 hours ago',
        ipAddress: '192.168.1.103',
      },
      {
        pcId: '4',
        pcName: 'LAB-PC-004',
        status: 'online',
        uptime: '12d 4h 22m',
        cpu: 23,
        memory: 41,
        lastSeen: 'Active now',
        ipAddress: '192.168.1.104',
      },
      {
        pcId: '5',
        pcName: 'LAB-PC-005',
        status: 'online',
        uptime: '1d 18h 45m',
        cpu: 56,
        memory: 73,
        lastSeen: 'Active now',
        ipAddress: '192.168.1.105',
      },
    ];

    return new Response(JSON.stringify({ success: true, systems }), {
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
