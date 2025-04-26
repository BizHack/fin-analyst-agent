
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartLine } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface TechnicalAnalysisProps {
  stock: string;
}

const TechnicalAnalysis = ({ stock }: TechnicalAnalysisProps) => {
  const technicalData = {
    AAPL: {
      summary: "Apple shows strong technical signals with the stock trading above both 50-day and 200-day moving averages. Multiple support levels have held in recent tests. Current price action suggests consolidation after the recent breakout above $198, with significant resistance at $210. RSI indicates slightly overbought conditions at 72.",
      patterns: [
        { name: "Recent Breakout", status: "Confirmed", confidence: "High", target: "$215" },
        { name: "Cup and Handle", status: "Forming", confidence: "Medium", target: "$225" },
        { name: "Support Level", status: "Holding", confidence: "High", target: "$195" },
        { name: "Resistance Level", status: "Testing", confidence: "Medium", target: "$210" }
      ],
      chartData: [
        { date: "Apr 1", price: 192.5, ma50: 190.2, ma200: 185.4, volume: 58 },
        { date: "Apr 5", price: 193.8, ma50: 190.5, ma200: 185.7, volume: 62 },
        { date: "Apr 10", price: 197.2, ma50: 191.0, ma200: 186.0, volume: 78 },
        { date: "Apr 15", price: 198.5, ma50: 191.8, ma200: 186.4, volume: 84 },
        { date: "Apr 20", price: 204.3, ma50: 192.5, ma200: 186.8, volume: 125 },
        { date: "Apr 25", price: 203.1, ma50: 193.2, ma200: 187.2, volume: 72 }
      ]
    },
    MSFT: {
      summary: "Microsoft displays a strong uptrend on multiple timeframes with accelerating momentum. The stock successfully tested the 50-day moving average on April 10th and has since formed higher highs and higher lows. Key resistance at $427 has been broken, suggesting further upside potential. RSI at 67 shows bullish momentum without being extremely overbought.",
      patterns: [
        { name: "Channel Breakout", status: "Confirmed", confidence: "High", target: "$445" },
        { name: "Golden Cross", status: "Active", confidence: "High", target: "N/A" },
        { name: "Support Level", status: "Holding", confidence: "High", target: "$418" },
        { name: "Resistance Level", status: "Broken", confidence: "High", target: "$427" }
      ],
      chartData: [
        { date: "Apr 1", price: 415.6, ma50: 410.2, ma200: 399.5, volume: 65 },
        { date: "Apr 5", price: 418.2, ma50: 411.4, ma200: 400.2, volume: 58 },
        { date: "Apr 10", price: 415.8, ma50: 412.3, ma200: 400.8, volume: 72 },
        { date: "Apr 15", price: 421.5, ma50: 413.0, ma200: 401.5, volume: 67 },
        { date: "Apr 20", price: 428.3, ma50: 414.1, ma200: 402.2, volume: 95 },
        { date: "Apr 25", price: 431.7, ma50: 415.4, ma200: 403.0, volume: 88 }
      ]
    },
    GOOGL: {
      summary: "Alphabet is showing mixed technical signals with the stock trading in a narrowing range between $170 and $180. Currently sitting just above the 50-day moving average but with declining momentum. Volume has been below average on recent rallies, suggesting weak conviction. MACD shows potential negative crossover while RSI at 54 is neutral.",
      patterns: [
        { name: "Pennant Pattern", status: "Forming", confidence: "Medium", target: "Undefined" },
        { name: "Support Level", status: "Testing", confidence: "Medium", target: "$172.50" },
        { name: "Resistance Level", status: "Holding", confidence: "High", target: "$180" },
        { name: "Volume Trend", status: "Declining", confidence: "Medium", target: "N/A" }
      ],
      chartData: [
        { date: "Apr 1", price: 176.8, ma50: 175.2, ma200: 169.4, volume: 68 },
        { date: "Apr 5", price: 178.2, ma50: 175.5, ma200: 169.7, volume: 72 },
        { date: "Apr 10", price: 179.5, ma50: 175.8, ma200: 170.1, volume: 65 },
        { date: "Apr 15", price: 177.3, ma50: 176.0, ma200: 170.5, volume: 55 },
        { date: "Apr 20", price: 174.5, ma50: 175.8, ma200: 170.8, volume: 58 },
        { date: "Apr 25", price: 173.8, ma50: 175.6, ma200: 171.2, volume: 50 }
      ]
    },
    AMZN: {
      summary: "Amazon is displaying a bullish technical setup with a recent breakout above the $180 resistance level. The stock is trading well above both the 50-day and 200-day moving averages with steadily increasing volume. Multiple technical indicators confirm the bullish momentum, though the stock is approaching overbought territory with RSI at 68.",
      patterns: [
        { name: "Breakout", status: "Confirmed", confidence: "High", target: "$195" },
        { name: "Support Level", status: "Established", confidence: "High", target: "$180" },
        { name: "Resistance Level", status: "Target", confidence: "Medium", target: "$195" },
        { name: "Volume Trend", status: "Increasing", confidence: "High", target: "N/A" }
      ],
      chartData: [
        { date: "Apr 1", price: 174.5, ma50: 171.2, ma200: 165.7, volume: 72 },
        { date: "Apr 5", price: 176.8, ma50: 172.0, ma200: 166.1, volume: 68 },
        { date: "Apr 10", price: 179.2, ma50: 172.8, ma200: 166.5, volume: 75 },
        { date: "Apr 15", price: 182.5, ma50: 173.6, ma200: 167.0, volume: 98 },
        { date: "Apr 20", price: 186.3, ma50: 174.7, ma200: 167.5, volume: 115 },
        { date: "Apr 25", price: 188.7, ma50: 175.8, ma200: 168.0, volume: 105 }
      ]
    },
    TSLA: {
      summary: "Tesla shows highly volatile price action with recent bearish momentum. The stock has broken below the key 200-day moving average and is testing the psychological $150 support level. Volume has been significantly higher on down days, suggesting distribution. The RSI at 38 is approaching oversold territory but doesn't yet indicate a reversal.",
      patterns: [
        { name: "Head & Shoulders", status: "Confirming", confidence: "Medium", target: "$135" },
        { name: "Support Level", status: "Testing", confidence: "High", target: "$150" },
        { name: "Moving Avg", status: "Bearish Cross", confidence: "High", target: "N/A" },
        { name: "Volume Pattern", status: "Distribution", confidence: "High", target: "N/A" }
      ],
      chartData: [
        { date: "Apr 1", price: 165.8, ma50: 170.5, ma200: 163.2, volume: 85 },
        { date: "Apr 5", price: 160.2, ma50: 169.8, ma200: 163.0, volume: 95 },
        { date: "Apr 10", price: 157.5, ma50: 168.2, ma200: 162.8, volume: 110 },
        { date: "Apr 15", price: 152.8, ma50: 166.5, ma200: 162.5, volume: 125 },
        { date: "Apr 20", price: 148.3, ma50: 164.7, ma200: 162.2, volume: 135 },
        { date: "Apr 25", price: 151.2, ma50: 163.0, ma200: 161.8, volume: 115 }
      ]
    }
  };

  const data = technicalData[stock as keyof typeof technicalData] || technicalData.AAPL;
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center">
            <ChartLine className="h-5 w-5 mr-2 text-teal" />
            Technical Analysis - {stock}
          </CardTitle>
          <CardDescription>Price action and technical patterns</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-6">{data.summary}</p>
          
          <div className="h-64 md:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" domain={['auto', 'auto']} />
                <YAxis yAxisId="right" orientation="right" domain={[0, 'dataMax + 30']} />
                <Tooltip />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="price" 
                  stroke="#33C3F0" 
                  strokeWidth={2.5} 
                  dot={{ r: 4 }} 
                  activeDot={{ r: 6 }} 
                />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="ma50" 
                  stroke="#16A34A" 
                  strokeWidth={1.5} 
                  dot={false} 
                />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="ma200" 
                  stroke="#DC2626" 
                  strokeWidth={1.5} 
                  dot={false} 
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#9CA3AF" 
                  strokeWidth={1} 
                  dot={false} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
      
      <Card className="shadow-md">
        <CardHeader>
          <CardTitle>Technical Patterns</CardTitle>
          <CardDescription>Detected chart patterns and signals</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-5">
            {data.patterns.map((pattern, index) => (
              <div key={index} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div className="flex justify-between mb-2">
                  <h3 className="font-medium">{pattern.name}</h3>
                  <span className={`text-sm px-2 py-0.5 rounded-full ${
                    pattern.confidence === 'High' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {pattern.confidence}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Status: {pattern.status}</span>
                  <span className="font-medium">Target: {pattern.target}</span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 bg-gray-50 p-4 rounded-md border border-gray-100">
            <h3 className="text-sm font-medium mb-2">Key Technical Levels</h3>
            <div className="space-y-2 text-sm">
              {stock === 'AAPL' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance:</span>
                    <span>$210, $215, $225</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span>$198, $195, $185</span>
                  </div>
                </>
              )}
              {stock === 'MSFT' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance:</span>
                    <span>$435, $445, $455</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span>$425, $418, $410</span>
                  </div>
                </>
              )}
              {stock === 'GOOGL' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance:</span>
                    <span>$175, $180, $183</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span>$172.50, $170, $167</span>
                  </div>
                </>
              )}
              {stock === 'AMZN' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance:</span>
                    <span>$190, $195, $200</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span>$185, $180, $175</span>
                  </div>
                </>
              )}
              {stock === 'TSLA' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resistance:</span>
                    <span>$155, $160, $170</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span>$150, $145, $135</span>
                  </div>
                </>
              )}
              <div className="flex justify-between pt-1">
                <span className="text-gray-600">RSI:</span>
                <span className={`${
                  (stock === 'AAPL' || stock === 'MSFT' || stock === 'AMZN') 
                    ? 'text-amber-600' 
                    : stock === 'TSLA' 
                    ? 'text-red-600' 
                    : 'text-gray-800'
                }`}>
                  {stock === 'AAPL' && '72 (Overbought)'}
                  {stock === 'MSFT' && '67 (Bullish)'}
                  {stock === 'GOOGL' && '54 (Neutral)'}
                  {stock === 'AMZN' && '68 (Bullish)'}
                  {stock === 'TSLA' && '38 (Bearish)'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TechnicalAnalysis;
