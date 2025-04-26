
import { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import SentimentAnalysis from "./dashboard/SentimentAnalysis";
import PoliticianTrades from "./dashboard/PoliticianTrades";
import TechnicalAnalysis from "./dashboard/TechnicalAnalysis";
import FundamentalAnalysis from "./dashboard/FundamentalAnalysis";

const DashboardTabs = () => {
  const [selectedStock, setSelectedStock] = useState("AAPL");
  
  const stocks = [
    { symbol: "AAPL", name: "Apple Inc." },
    { symbol: "MSFT", name: "Microsoft Corp." },
    { symbol: "GOOGL", name: "Alphabet Inc." },
    { symbol: "AMZN", name: "Amazon.com Inc." },
    { symbol: "TSLA", name: "Tesla Inc." }
  ];
  
  return (
    <div className="mt-8">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-semibold text-midnight mb-4 sm:mb-0">Market Intelligence</h2>
        
        <div className="flex items-center">
          <label htmlFor="stock-select" className="text-sm font-medium mr-3">
            Selected Stock:
          </label>
          <select
            id="stock-select"
            value={selectedStock}
            onChange={(e) => setSelectedStock(e.target.value)}
            className="bg-white border border-gray-200 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-transparent"
          >
            {stocks.map(stock => (
              <option key={stock.symbol} value={stock.symbol}>
                {stock.symbol} - {stock.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <Tabs defaultValue="sentiment" className="w-full">
        <TabsList className="grid grid-cols-4 mb-8 bg-transparent">
          <TabsTrigger 
            value="sentiment" 
            className="data-[state=active]:text-teal data-[state=active]:border-b-2 data-[state=active]:border-teal rounded-none bg-transparent"
          >
            Sentiment
          </TabsTrigger>
          <TabsTrigger 
            value="politicians" 
            className="data-[state=active]:text-teal data-[state=active]:border-b-2 data-[state=active]:border-teal rounded-none bg-transparent"
          >
            Politician Trades
          </TabsTrigger>
          <TabsTrigger 
            value="technical" 
            className="data-[state=active]:text-teal data-[state=active]:border-b-2 data-[state=active]:border-teal rounded-none bg-transparent"
          >
            Technical Analysis
          </TabsTrigger>
          <TabsTrigger 
            value="fundamental" 
            className="data-[state=active]:text-teal data-[state=active]:border-b-2 data-[state=active]:border-teal rounded-none bg-transparent"
          >
            Fundamentals
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="sentiment" className="animate-fade-in">
          <SentimentAnalysis stock={selectedStock} />
        </TabsContent>
        
        <TabsContent value="politicians" className="animate-fade-in">
          <PoliticianTrades stock={selectedStock} />
        </TabsContent>
        
        <TabsContent value="technical" className="animate-fade-in">
          <TechnicalAnalysis stock={selectedStock} />
        </TabsContent>
        
        <TabsContent value="fundamental" className="animate-fade-in">
          <FundamentalAnalysis stock={selectedStock} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardTabs;
