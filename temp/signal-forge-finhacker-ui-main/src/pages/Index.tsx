
import MarketMonitor from "@/components/MarketMonitor";
import DashboardTabs from "@/components/DashboardTabs";

const Index = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="bg-midnight text-white">
        <div className="container mx-auto px-4 py-12 md:py-20">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="mb-8 md:mb-0">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 animate-fade-in">
                <span className="text-white">Fin</span>
                <span className="text-teal">Hacker</span>
              </h1>
              <p className="text-lg md:text-xl text-gray-300 animate-fade-in">
                Decoding Signals from Politics, Markets, and Social Media
              </p>
            </div>
            
            <div className="w-full md:w-auto">
              <MarketMonitor />
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="container mx-auto px-4 py-6 md:py-10">
        <DashboardTabs />
      </div>
    </div>
  );
};

export default Index;
