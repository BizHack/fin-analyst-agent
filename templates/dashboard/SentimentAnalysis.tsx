import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, X } from "lucide-react";

interface SentimentAnalysisProps {
  stock: string;
}

const SentimentAnalysis = ({ stock }: SentimentAnalysisProps) => {
  const sentimentData = {
    AAPL: {
      reddit: { positive: 65, neutral: 25, negative: 10 },
      twitter: { positive: 58, neutral: 22, negative: 20 },
      truth: { positive: 72, neutral: 18, negative: 10 },
      summary: "Overall bullish sentiment across social platforms with 65% positive mentions on Reddit. Recent product announcements have generated excitement, though some concerns about valuation remain. Twitter sentiment shows more mixed opinions with 20% negative comments primarily focused on supply chain concerns."
    },
    MSFT: {
      reddit: { positive: 72, neutral: 18, negative: 10 },
      twitter: { positive: 68, neutral: 22, negative: 10 },
      truth: { positive: 55, neutral: 35, negative: 10 },
      summary: "Strongly positive sentiment across all platforms with Reddit showing 72% positive mentions. AI initiatives and cloud services growth are driving enthusiastic discussions. Most negative sentiment relates to pricing concerns for enterprise customers."
    },
    GOOGL: {
      reddit: { positive: 58, neutral: 22, negative: 20 },
      twitter: { positive: 52, neutral: 28, negative: 20 },
      truth: { positive: 48, neutral: 32, negative: 20 },
      summary: "Mixed sentiment with moderately positive bias. Reddit shows 58% positive mentions but a notable 20% negative sentiment related to regulatory concerns. Many discussions focus on AI competition with mixed opinions on Google's position versus competitors."
    },
    AMZN: {
      reddit: { positive: 62, neutral: 25, negative: 13 },
      twitter: { positive: 58, neutral: 27, negative: 15 },
      truth: { positive: 65, neutral: 20, negative: 15 },
      summary: "Generally positive sentiment with 62% favorable mentions on Reddit. E-commerce dominance and AWS growth are key positive topics. Employee treatment and market power concerns drive most negative discussions."
    },
    TSLA: {
      reddit: { positive: 45, neutral: 15, negative: 40 },
      twitter: { positive: 48, neutral: 12, negative: 40 },
      truth: { positive: 68, neutral: 17, negative: 15 },
      summary: "Highly polarized sentiment with significant division between platforms. Reddit shows nearly equal positive (45%) and negative (40%) sentiment. Twitter reflects similar division, while Truth Social skews more positive at 68%. CEO statements and production targets drive most discussions."
    },
  };

  const data = sentimentData[stock as keyof typeof sentimentData] || sentimentData.AAPL;
  const platforms = [
    { name: "Reddit", icon: MessageSquare, data: data.reddit },
    { name: "X", icon: X, data: data.twitter },
    { name: "Truth Social", icon: MessageSquare, data: data.truth },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 shadow-md">
        <CardHeader>
          <CardTitle>Sentiment Analysis for {stock}</CardTitle>
          <CardDescription>Analysis of social media sentiment across platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-6">{data.summary}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {platforms.map((platform) => (
              <div key={platform.name} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-3">
                  <platform.icon className="h-5 w-5 mr-2 text-gray-600" />
                  <h3 className="font-medium">{platform.name}</h3>
                </div>
                
                <div className="space-y-2">
                  <SentimentBar 
                    label="Positive" 
                    percentage={platform.data.positive} 
                    color="bg-green-500" 
                  />
                  <SentimentBar 
                    label="Neutral" 
                    percentage={platform.data.neutral} 
                    color="bg-gray-400" 
                  />
                  <SentimentBar 
                    label="Negative" 
                    percentage={platform.data.negative} 
                    color="bg-red-500" 
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      <Card className="shadow-md">
        <CardHeader>
          <CardTitle>Key Topics</CardTitle>
          <CardDescription>Most discussed topics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <TopicItem 
              topic="Product Announcements" 
              sentiment="Positive" 
              sentimentColor="text-green-500" 
              mentions={234} 
            />
            <TopicItem 
              topic="Quarterly Earnings" 
              sentiment="Neutral" 
              sentimentColor="text-gray-500" 
              mentions={187} 
            />
            <TopicItem 
              topic="Market Competition" 
              sentiment="Mixed" 
              sentimentColor="text-amber-500" 
              mentions={156} 
            />
            <TopicItem 
              topic="Leadership Changes" 
              sentiment="Negative" 
              sentimentColor="text-red-500" 
              mentions={98} 
            />
            <TopicItem 
              topic="Partnerships" 
              sentiment="Positive" 
              sentimentColor="text-green-500" 
              mentions={76} 
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const SentimentBar = ({ label, percentage, color }: { label: string; percentage: number; color: string }) => {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="font-medium">{percentage}%</span>
      </div>
      <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color}`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

const TopicItem = ({ 
  topic, 
  sentiment, 
  sentimentColor, 
  mentions 
}: { 
  topic: string; 
  sentiment: string; 
  sentimentColor: string; 
  mentions: number 
}) => {
  return (
    <div className="flex items-center justify-between border-b border-gray-100 pb-2">
      <div>
        <p className="font-medium">{topic}</p>
        <p className={`text-sm ${sentimentColor}`}>{sentiment}</p>
      </div>
      <div className="text-sm text-gray-500">
        {mentions} mentions
      </div>
    </div>
  );
};

export default SentimentAnalysis;
