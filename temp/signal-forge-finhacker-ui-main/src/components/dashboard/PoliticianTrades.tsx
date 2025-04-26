
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users } from "lucide-react";

interface PoliticianTradesProps {
  stock: string;
}

const PoliticianTrades = ({ stock }: PoliticianTradesProps) => {
  const tradesData = {
    AAPL: {
      summary: "Recent congressional trading activity shows 7 purchases and 3 sales of Apple stock in the last 30 days. Most notable was a $250,000 purchase by Rep. Johnson on April 10th, following the tech committee hearing. Senator Wallace sold $180,000 worth just before the quarterly earnings announcement.",
      trades: [
        { politician: "Rep. Michael Johnson", party: "R", date: "Apr 10, 2025", action: "BUY", amount: "$250,000", timing: "After tech committee" },
        { politician: "Sen. Maria Wallace", party: "D", date: "Apr 15, 2025", action: "SELL", amount: "$180,000", timing: "Pre-earnings" },
        { politician: "Rep. Thomas Lee", party: "D", date: "Apr 8, 2025", action: "BUY", amount: "$75,000", timing: "After product launch" },
        { politician: "Sen. Robert Wilson", party: "R", date: "Apr 12, 2025", action: "BUY", amount: "$120,000", timing: "Standard disclosure" },
        { politician: "Rep. Sarah Martinez", party: "D", date: "Apr 14, 2025", action: "SELL", amount: "$95,000", timing: "Portfolio rebalance" }
      ]
    },
    MSFT: {
      summary: "Microsoft stock saw balanced congressional trading with 5 purchases and 4 sales in the past month. Largest transaction was a $340,000 purchase by Sen. Reynolds following the AI summit. Notable cluster of buying activity occurred after the government contract announcement.",
      trades: [
        { politician: "Sen. James Reynolds", party: "R", date: "Apr 8, 2025", action: "BUY", amount: "$340,000", timing: "After AI summit" },
        { politician: "Rep. Lisa Chen", party: "D", date: "Apr 11, 2025", action: "BUY", amount: "$125,000", timing: "After gov't contract" },
        { politician: "Sen. Daniel Moore", party: "R", date: "Apr 14, 2025", action: "SELL", amount: "$230,000", timing: "Annual disclosure" },
        { politician: "Rep. Kevin Wright", party: "D", date: "Apr 9, 2025", action: "BUY", amount: "$80,000", timing: "After committee" },
        { politician: "Sen. Patricia Lopez", party: "D", date: "Apr 16, 2025", action: "SELL", amount: "$175,000", timing: "Portfolio adjustment" }
      ]
    },
    GOOGL: {
      summary: "Alphabet stock saw more selling than buying from politicians with 2 purchases and 6 sales. Most significant was a $420,000 sale by Rep. Thompson prior to the antitrust hearing. Buying activity was minimal compared to other tech stocks in the same period.",
      trades: [
        { politician: "Rep. William Thompson", party: "R", date: "Apr 10, 2025", action: "SELL", amount: "$420,000", timing: "Before antitrust hearing" },
        { politician: "Sen. Jennifer Brown", party: "D", date: "Apr 12, 2025", action: "SELL", amount: "$265,000", timing: "Standard disclosure" },
        { politician: "Rep. David Garcia", party: "D", date: "Apr 9, 2025", action: "BUY", amount: "$110,000", timing: "After earnings call" },
        { politician: "Sen. Richard Taylor", party: "R", date: "Apr 15, 2025", action: "SELL", amount: "$195,000", timing: "Regular trading" },
        { politician: "Rep. Elizabeth Wilson", party: "D", date: "Apr 14, 2025", action: "SELL", amount: "$85,000", timing: "Annual disclosure" }
      ]
    },
    AMZN: {
      summary: "Amazon stock was heavily bought by congressional members with 9 purchases and only 2 sales. Largest transaction was a $380,000 purchase by Sen. Miller just before the AWS government contract announcement. Unusual buying pattern observed compared to historical data.",
      trades: [
        { politician: "Sen. Christopher Miller", party: "R", date: "Apr 7, 2025", action: "BUY", amount: "$380,000", timing: "Before AWS contract" },
        { politician: "Rep. Susan Martin", party: "D", date: "Apr 10, 2025", action: "BUY", amount: "$220,000", timing: "After committee meeting" },
        { politician: "Sen. Andrew Wilson", party: "R", date: "Apr 14, 2025", action: "BUY", amount: "$175,000", timing: "Standard filing" },
        { politician: "Rep. Michelle Lee", party: "D", date: "Apr 9, 2025", action: "SELL", amount: "$145,000", timing: "Portfolio rebalance" },
        { politician: "Sen. John Adams", party: "R", date: "Apr 13, 2025", action: "BUY", amount: "$210,000", timing: "Regular disclosure" }
      ]
    },
    TSLA: {
      summary: "Tesla stock showed polarized political trading patterns with Republicans mostly buying (7 transactions) and Democrats mostly selling (5 transactions). Most significant was a $520,000 purchase by Rep. Harrison after meeting with the CEO. Trading volume was higher than any other stock in the dataset.",
      trades: [
        { politician: "Rep. Gregory Harrison", party: "R", date: "Apr 11, 2025", action: "BUY", amount: "$520,000", timing: "After CEO meeting" },
        { politician: "Sen. Rebecca Chen", party: "D", date: "Apr 13, 2025", action: "SELL", amount: "$310,000", timing: "Portfolio adjustment" },
        { politician: "Rep. Michael Perry", party: "R", date: "Apr 8, 2025", action: "BUY", amount: "$290,000", timing: "After factory tour" },
        { politician: "Sen. Linda Martinez", party: "D", date: "Apr 15, 2025", action: "SELL", amount: "$240,000", timing: "Standard disclosure" },
        { politician: "Rep. Thomas Baker", party: "R", date: "Apr 12, 2025", action: "BUY", amount: "$185,000", timing: "Annual filing" }
      ]
    }
  };
  
  const data = tradesData[stock as keyof typeof tradesData] || tradesData.AAPL;
  
  return (
    <Card className="shadow-md">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Users className="h-5 w-5 mr-2 text-teal" />
          Political Trading Activity - {stock}
        </CardTitle>
        <CardDescription>Recent congressional stock transactions</CardDescription>
      </CardHeader>
      
      <CardContent>
        <p className="text-gray-700 mb-6">{data.summary}</p>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4">Politician</th>
                <th className="text-left py-3 px-4">Party</th>
                <th className="text-left py-3 px-4">Date</th>
                <th className="text-left py-3 px-4">Action</th>
                <th className="text-right py-3 px-4">Amount</th>
                <th className="text-left py-3 px-4">Context</th>
              </tr>
            </thead>
            <tbody>
              {data.trades.map((trade, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="py-3 px-4">{trade.politician}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-block rounded-full w-5 h-5 ${
                      trade.party === 'D' ? 'bg-blue-500' : 'bg-red-500'
                    }`}></span>
                  </td>
                  <td className="py-3 px-4">{trade.date}</td>
                  <td className="py-3 px-4">
                    <span className={`font-medium ${
                      trade.action === 'BUY' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {trade.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-medium">{trade.amount}</td>
                  <td className="py-3 px-4 text-gray-600 text-sm">{trade.timing}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="mt-6 bg-gray-50 p-4 rounded-md border border-gray-100">
          <h3 className="text-sm font-medium mb-2">Trading Pattern Analysis</h3>
          <p className="text-sm text-gray-600">
            {stock === 'AAPL' && 'Unusual buying activity detected before product announcements. Correlation with committee assignments observed.'}
            {stock === 'MSFT' && 'Balanced trading with slight buy bias. Trading activity shows moderate correlation with public announcements.'}
            {stock === 'GOOGL' && 'Strong sell bias detected. Trading timing suggests potential information advantage around regulatory events.'}
            {stock === 'AMZN' && 'Very strong buy signal from congressional activity. Unusual pattern compared to historical data for this stock.'}
            {stock === 'TSLA' && 'Highly partisan trading pattern. Volume significantly above average suggesting high confidence positioning.'}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default PoliticianTrades;
