import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Bitcoin, DollarSign, X } from "lucide-react";

interface AssetPrice {
  symbol: string;
  price: number;
  change: number;
  name: string;
}

const MarketMonitor = () => {
  const [prices, setPrices] = useState<AssetPrice[]>([
    { symbol: "SPY", price: 504.23, change: 0.65, name: "S&P 500" },
    { symbol: "BTC", price: 63458.75, change: -1.23, name: "Bitcoin" },
    { symbol: "GOLD", price: 2342.80, change: 0.34, name: "Gold" },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setPrices(prevPrices => 
        prevPrices.map(asset => ({
          ...asset,
          price: asset.price * (1 + (Math.random() * 0.002 - 0.001)),
          change: asset.change + (Math.random() * 0.2 - 0.1),
        }))
      );
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col sm:flex-row gap-2 animate-fade-in">
      {prices.map((asset) => (
        <Card key={asset.symbol} className="bg-white border-none shadow-sm">
          <CardContent className="p-3 flex items-center">
            <AssetIcon symbol={asset.symbol} />
            <div className="ml-3">
              <div className="flex items-center">
                <span className="font-semibold text-sm">{asset.symbol}</span>
                <span className="text-xs text-muted-foreground ml-2">{asset.name}</span>
              </div>
              <div className="flex items-center">
                <span className="font-medium">
                  ${asset.price.toLocaleString(undefined, { maximumFractionDigits: 2, minimumFractionDigits: 2 })}
                </span>
                <span 
                  className={`text-xs ml-2 flex items-center ${
                    asset.change >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {asset.change >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                  {asset.change.toFixed(2)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

const AssetIcon = ({ symbol }: { symbol: string }) => {
  switch (symbol) {
    case "BTC":
      return <Bitcoin className="h-6 w-6 text-amber-500" />;
    case "GOLD":
      return <div className="h-6 w-6 rounded-full bg-amber-400 flex items-center justify-center">
        <span className="text-xs font-bold text-amber-900">AU</span>
      </div>;
    default:
      return <DollarSign className="h-6 w-6 text-green-600" />;
  }
};

export default MarketMonitor;
