
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Banknote, ChartBar } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface FundamentalAnalysisProps {
  stock: string;
}

const FundamentalAnalysis = ({ stock }: FundamentalAnalysisProps) => {
  const fundamentalData = {
    AAPL: {
      summary: "Apple continues to display strong fundamental metrics with a 15% year-over-year revenue growth and expanding profit margins. Recent earnings call highlighted significant growth in services revenue, now accounting for 25% of total revenue. Management emphasized AI integration plans for upcoming product lines. Balance sheet remains exceptionally strong with $195B cash and short-term investments.",
      earningsCallSentiment: {
        positive: 72,
        negative: 8,
        neutral: 20,
        keyTopics: ["AI Integration", "Services Growth", "Share Repurchases", "Supply Chain", "Capital Returns"]
      },
      financialMetrics: {
        revenue: "Q1 2025: $96.5B (↑15%)",
        eps: "$1.58 (↑18%)",
        peRatio: "28.4x",
        dividendYield: "0.6%",
        debtToEquity: "1.2"
      },
      quarterlyData: [
        { quarter: "Q2 2024", revenue: 82.1, netIncome: 24.2, eps: 1.32 },
        { quarter: "Q3 2024", revenue: 85.4, netIncome: 24.8, eps: 1.35 },
        { quarter: "Q4 2024", revenue: 89.0, netIncome: 26.1, eps: 1.42 },
        { quarter: "Q1 2025", revenue: 96.5, netIncome: 29.5, eps: 1.58 }
      ]
    },
    MSFT: {
      summary: "Microsoft reported exceptional fundamental performance with Azure cloud services driving 22% year-over-year revenue growth. AI investments are beginning to monetize with significant enterprise adoption. Margins expanded despite increased R&D spending. Management guidance raised expectations for the next fiscal year, highlighting accelerating momentum in cloud and AI solutions.",
      earningsCallSentiment: {
        positive: 78,
        negative: 5,
        neutral: 17,
        keyTopics: ["Azure Growth", "AI Monetization", "Enterprise Adoption", "Gaming Strategy", "Margins"]
      },
      financialMetrics: {
        revenue: "Q1 2025: $54.8B (↑22%)",
        eps: "$2.95 (↑26%)",
        peRatio: "32.5x",
        dividendYield: "0.8%",
        debtToEquity: "0.5"
      },
      quarterlyData: [
        { quarter: "Q2 2024", revenue: 45.8, netIncome: 20.5, eps: 2.35 },
        { quarter: "Q3 2024", revenue: 48.2, netIncome: 21.7, eps: 2.45 },
        { quarter: "Q4 2024", revenue: 51.5, netIncome: 22.8, eps: 2.65 },
        { quarter: "Q1 2025", revenue: 54.8, netIncome: 24.1, eps: 2.95 }
      ]
    },
    GOOGL: {
      summary: "Alphabet reported mixed fundamentals with 18% revenue growth but declining margins due to aggressive AI investments. Search revenue remains strong while YouTube growth accelerated. Cloud division achieved profitability for the first time. Management faced numerous analyst questions about AI competition and the timeline for AI investment returns during the earnings call.",
      earningsCallSentiment: {
        positive: 55,
        negative: 15,
        neutral: 30,
        keyTopics: ["AI Investments", "Search Revenue", "Cloud Profitability", "YouTube Growth", "Regulatory Challenges"]
      },
      financialMetrics: {
        revenue: "Q1 2025: $78.2B (↑18%)",
        eps: "$1.89 (↑8%)",
        peRatio: "24.6x",
        dividendYield: "0.5%",
        debtToEquity: "0.3"
      },
      quarterlyData: [
        { quarter: "Q2 2024", revenue: 68.5, netIncome: 19.2, eps: 1.72 },
        { quarter: "Q3 2024", revenue: 72.1, netIncome: 19.8, eps: 1.75 },
        { quarter: "Q4 2024", revenue: 75.3, netIncome: 20.5, eps: 1.82 },
        { quarter: "Q1 2025", revenue: 78.2, netIncome: 21.4, eps: 1.89 }
      ]
    },
    AMZN: {
      summary: "Amazon delivered strong fundamentals with AWS reaccelerating to 25% growth and e-commerce margins improving significantly. Operating cash flow increased 35% year-over-year. Management highlighted progress in grocery and healthcare initiatives. Advertising revenue grew 30%, becoming increasingly material to overall results. AI services within AWS were emphasized as a key growth driver for future quarters.",
      earningsCallSentiment: {
        positive: 75,
        negative: 10,
        neutral: 15,
        keyTopics: ["AWS Growth", "Retail Margins", "Advertising Revenue", "AI Services", "Logistics Efficiency"]
      },
      financialMetrics: {
        revenue: "Q1 2025: $135.5B (↑17%)",
        eps: "$1.25 (↑42%)",
        peRatio: "38.2x",
        dividendYield: "N/A",
        debtToEquity: "0.6"
      },
      quarterlyData: [
        { quarter: "Q2 2024", revenue: 118.2, netIncome: 8.8, eps: 0.85 },
        { quarter: "Q3 2024", revenue: 122.5, netIncome: 9.5, eps: 0.92 },
        { quarter: "Q4 2024", revenue: 130.2, netIncome: 11.2, eps: 1.08 },
        { quarter: "Q1 2025", revenue: 135.5, netIncome: 13.0, eps: 1.25 }
      ]
    },
    TSLA: {
      summary: "Tesla reported weakening fundamentals with 5% revenue growth and margin compression due to price cuts and increased competition. Vehicle deliveries missed estimates by 8%. Energy storage business showed strong growth of 45%. Management provided vague timeline for new models and emphasized progress on autonomy. Significant time was devoted to robotics and AI projects during the earnings call.",
      earningsCallSentiment: {
        positive: 42,
        negative: 28,
        neutral: 30,
        keyTopics: ["Vehicle Margins", "Delivery Targets", "New Models", "Autonomy Progress", "Energy Storage"]
      },
      financialMetrics: {
        revenue: "Q1 2025: $22.8B (↑5%)",
        eps: "$0.62 (↓18%)",
        peRatio: "58.1x",
        dividendYield: "N/A",
        debtToEquity: "0.1"
      },
      quarterlyData: [
        { quarter: "Q2 2024", revenue: 23.1, netIncome: 3.2, eps: 0.78 },
        { quarter: "Q3 2024", revenue: 22.8, netIncome: 3.0, eps: 0.73 },
        { quarter: "Q4 2024", revenue: 22.2, netIncome: 2.7, eps: 0.65 },
        { quarter: "Q1 2025", revenue: 22.8, netIncome: 2.6, eps: 0.62 }
      ]
    }
  };

  const data = fundamentalData[stock as keyof typeof fundamentalData] || fundamentalData.AAPL;
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center">
            <ChartBar className="h-5 w-5 mr-2 text-teal" />
            Fundamental Analysis - {stock}
          </CardTitle>
          <CardDescription>Earnings reports and financial metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-6">{data.summary}</p>
          
          <h3 className="text-lg font-medium mb-4">Quarterly Performance</h3>
          <div className="h-64 md:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.quarterlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="quarter" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="revenue" name="Revenue ($B)" fill="#33C3F0" />
                <Bar yAxisId="left" dataKey="netIncome" name="Net Income ($B)" fill="#1A1F2C" />
                <Bar yAxisId="right" dataKey="eps" name="EPS ($)" fill="#16A34A" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <div>
              <h3 className="text-lg font-medium mb-3">Key Metrics</h3>
              <div className="space-y-2">
                <MetricItem label="Revenue" value={data.financialMetrics.revenue} />
                <MetricItem label="EPS" value={data.financialMetrics.eps} />
                <MetricItem label="P/E Ratio" value={data.financialMetrics.peRatio} />
                <MetricItem label="Dividend Yield" value={data.financialMetrics.dividendYield} />
                <MetricItem label="Debt-to-Equity" value={data.financialMetrics.debtToEquity} />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-3">Earnings Call Sentiment</h3>
              <div className="flex mb-4">
                <div className="h-2 bg-green-500" style={{ width: `${data.earningsCallSentiment.positive}%` }}></div>
                <div className="h-2 bg-gray-300" style={{ width: `${data.earningsCallSentiment.neutral}%` }}></div>
                <div className="h-2 bg-red-500" style={{ width: `${data.earningsCallSentiment.negative}%` }}></div>
              </div>
              <div className="flex justify-between text-sm mb-5">
                <span className="text-green-600">{data.earningsCallSentiment.positive}% Positive</span>
                <span className="text-gray-500">{data.earningsCallSentiment.neutral}% Neutral</span>
                <span className="text-red-600">{data.earningsCallSentiment.negative}% Negative</span>
              </div>
              
              <h4 className="text-sm font-medium mb-2">Key Topics Mentioned</h4>
              <div className="flex flex-wrap gap-2">
                {data.earningsCallSentiment.keyTopics.map((topic, index) => (
                  <span 
                    key={index}
                    className="bg-gray-100 px-3 py-1 rounded-full text-sm"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card className="shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Banknote className="h-5 w-5 mr-2 text-teal" />
            Analyst Consensus
          </CardTitle>
          <CardDescription>Wall Street expectations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center mb-5">
            <div className="w-32 h-32 rounded-full border-8 border-teal flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {stock === 'AAPL' && 'BUY'}
                  {stock === 'MSFT' && 'STRONG BUY'}
                  {stock === 'GOOGL' && 'BUY'}
                  {stock === 'AMZN' && 'BUY'}
                  {stock === 'TSLA' && 'HOLD'}
                </div>
                <div className="text-sm text-gray-500">Consensus</div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Price Target</span>
                <span className="font-medium">
                  {stock === 'AAPL' && '$225 (+10%)'}
                  {stock === 'MSFT' && '$455 (+6%)'}
                  {stock === 'GOOGL' && '$190 (+9%)'}
                  {stock === 'AMZN' && '$210 (+11%)'}
                  {stock === 'TSLA' && '$160 (+6%)'}
                </span>
              </div>
              <div className="h-1.5 w-full bg-gray-200 rounded-full">
                <div 
                  className="h-1.5 bg-teal rounded-full" 
                  style={{ 
                    width: stock === 'MSFT' ? '85%' : 
                           stock === 'TSLA' ? '55%' : '75%' 
                  }}
                ></div>
              </div>
            </div>
            
            <AnalystRating 
              label="Strong Buy" 
              count={
                stock === 'AAPL' ? 18 : 
                stock === 'MSFT' ? 24 : 
                stock === 'GOOGL' ? 16 : 
                stock === 'AMZN' ? 21 : 10
              } 
              total={35} 
            />
            <AnalystRating 
              label="Buy" 
              count={
                stock === 'AAPL' ? 12 : 
                stock === 'MSFT' ? 9 : 
                stock === 'GOOGL' ? 14 : 
                stock === 'AMZN' ? 10 : 12
              } 
              total={35} 
            />
            <AnalystRating 
              label="Hold" 
              count={
                stock === 'AAPL' ? 4 : 
                stock === 'MSFT' ? 2 : 
                stock === 'GOOGL' ? 4 : 
                stock === 'AMZN' ? 3 : 10
              } 
              total={35} 
            />
            <AnalystRating 
              label="Sell" 
              count={
                stock === 'AAPL' ? 1 : 
                stock === 'MSFT' ? 0 : 
                stock === 'GOOGL' ? 1 : 
                stock === 'AMZN' ? 1 : 3
              } 
              total={35} 
            />
          </div>
          
          <div className="mt-6 space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Revenue Est (FY25)</span>
              <span className="font-medium">
                {stock === 'AAPL' && '$390.2B'}
                {stock === 'MSFT' && '$245.5B'}
                {stock === 'GOOGL' && '$335.8B'}
                {stock === 'AMZN' && '$610.2B'}
                {stock === 'TSLA' && '$95.7B'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">EPS Est (FY25)</span>
              <span className="font-medium">
                {stock === 'AAPL' && '$6.85'}
                {stock === 'MSFT' && '$12.45'}
                {stock === 'GOOGL' && '$8.25'}
                {stock === 'AMZN' && '$5.40'}
                {stock === 'TSLA' && '$2.85'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Growth Est (5yr)</span>
              <span className="font-medium">
                {stock === 'AAPL' && '12.5%'}
                {stock === 'MSFT' && '15.2%'}
                {stock === 'GOOGL' && '14.8%'}
                {stock === 'AMZN' && '18.5%'}
                {stock === 'TSLA' && '22.5%'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const MetricItem = ({ label, value }: { label: string; value: string }) => {
  return (
    <div className="flex justify-between items-center border-b border-gray-100 pb-2">
      <span className="text-gray-600">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
};

const AnalystRating = ({ label, count, total }: { label: string; count: number; total: number }) => {
  const percentage = (count / total) * 100;
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{count}/{total}</span>
      </div>
      <div className="h-1.5 w-full bg-gray-200 rounded-full">
        <div 
          className="h-1.5 bg-teal rounded-full" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default FundamentalAnalysis;
