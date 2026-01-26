import "jsr:@supabase/functions-js/edge-runtime.d.ts";

interface DiskData {
  pcId: string;
  pcName: string;
  totalSpace: string;
  usedSpace: string;
  freeSpace: string;
  usagePercent: number;
  status: 'healthy' | 'warning' | 'critical';
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

    const diskData: DiskData[] = [
      {
        pcId: '1',
        pcName: 'LAB-PC-001',
        totalSpace: '500 GB',
        usedSpace: '320 GB',
        freeSpace: '180 GB',
        usagePercent: 64,
        status: 'healthy',
      },
      {
        pcId: '2',
        pcName: 'LAB-PC-002',
        totalSpace: '1 TB',
        usedSpace: '850 GB',
        freeSpace: '150 GB',
        usagePercent: 85,
        status: 'warning',
      },
      {
        pcId: '3',
        pcName: 'LAB-PC-003',
        totalSpace: '500 GB',
        usedSpace: '475 GB',
        freeSpace: '25 GB',
        usagePercent: 95,
        status: 'critical',
      },
      {
        pcId: '4',
        pcName: 'LAB-PC-004',
        totalSpace: '750 GB',
        usedSpace: '300 GB',
        freeSpace: '450 GB',
        usagePercent: 40,
        status: 'healthy',
      },
      {
        pcId: '5',
        pcName: 'LAB-PC-005',
        totalSpace: '1 TB',
        usedSpace: '400 GB',
        freeSpace: '600 GB',
        usagePercent: 40,
        status: 'healthy',
      },
    ];

    return new Response(JSON.stringify({ success: true, diskData }), {
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
