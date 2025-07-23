import React, { useState, useEffect } from 'react';
import { Report, ReportTemplate, AnalyticsDashboard } from '../types/reports';
import { reportsService } from '../services/reportsService';
import { 
  DocumentChartBarIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  HomeIcon,
  UserGroupIcon,
  WrenchScrewdriverIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'reports' | 'analytics' | 'templates'>('reports');
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [reportsData, templatesData, analyticsData] = await Promise.all([
        reportsService.getReports(),
        reportsService.getReportTemplates(),
        reportsService.getAnalyticsDashboard(dateRange.startDate, dateRange.endDate),
      ]);

      setReports(reportsData);
      setTemplates(templatesData);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error fetching reports data:', error);
      toast.error('Failed to load reports data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (type: string) => {
    try {
      let report;
      switch (type) {
        case 'financial':
          report = await reportsService.generateFinancialReport(dateRange.startDate, dateRange.endDate);
          break;
        case 'occupancy':
          report = await reportsService.generateOccupancyReport(dateRange.startDate, dateRange.endDate);
          break;
        case 'maintenance':
          report = await reportsService.generateMaintenanceReport(dateRange.startDate, dateRange.endDate);
          break;
        case 'tenant':
          report = await reportsService.generateTenantReport(dateRange.startDate, dateRange.endDate);
          break;
        case 'property':
          report = await reportsService.generatePropertyReport(dateRange.startDate, dateRange.endDate);
          break;
        default:
          throw new Error('Unknown report type');
      }
      
      setReports([report, ...reports]);
      toast.success('Report generated successfully');
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    }
  };

  const handleDownloadReport = async (reportId: string) => {
    try {
      const blob = await reportsService.downloadReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Report downloaded successfully');
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error('Failed to download report');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'financial':
        return CurrencyDollarIcon;
      case 'occupancy':
        return HomeIcon;
      case 'maintenance':
        return WrenchScrewdriverIcon;
      case 'tenant':
        return UserGroupIcon;
      case 'property':
        return BuildingOfficeIcon;
      default:
        return DocumentTextIcon;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            Reports & Analytics
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Generate insights and reports for your rental properties
          </p>
        </div>
        <div className="mt-4 flex space-x-3 md:ml-4 md:mt-0">
          <button
            type="button"
            onClick={() => console.log('Schedule report')}
            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            <CalendarDaysIcon className="h-4 w-4 mr-2" />
            Schedule
          </button>
          <button
            type="button"
            onClick={() => console.log('Create custom report')}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Custom Report
          </button>
        </div>
      </div>

      {/* Date Range Filter */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <CalendarDaysIcon className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-700">Date Range:</span>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="date"
              value={dateRange.startDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.endDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'reports', name: 'Reports', icon: DocumentChartBarIcon },
            { id: 'analytics', name: 'Analytics', icon: ChartBarIcon },
            { id: 'templates', name: 'Templates', icon: DocumentTextIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`${
                activeTab === tab.id
                  ? 'border-green-500 text-green-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              } flex items-center whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium`}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Reports Tab */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Quick Report Generation */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Reports</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {[
                { type: 'financial', name: 'Financial Report', icon: CurrencyDollarIcon, color: 'green' },
                { type: 'occupancy', name: 'Occupancy Report', icon: HomeIcon, color: 'blue' },
                { type: 'maintenance', name: 'Maintenance Report', icon: WrenchScrewdriverIcon, color: 'orange' },
                { type: 'tenant', name: 'Tenant Report', icon: UserGroupIcon, color: 'purple' },
                { type: 'property', name: 'Property Report', icon: BuildingOfficeIcon, color: 'indigo' },
              ].map((report) => (
                <button
                  key={report.type}
                  onClick={() => handleGenerateReport(report.type)}
                  className={`p-4 border-2 border-dashed border-${report.color}-300 rounded-lg hover:border-${report.color}-400 hover:bg-${report.color}-50 transition-colors`}
                >
                  <report.icon className={`h-8 w-8 text-${report.color}-600 mx-auto mb-2`} />
                  <p className="text-sm font-medium text-gray-900">{report.name}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Recent Reports */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Recent Reports
              </h3>
              {reports.length === 0 ? (
                <div className="text-center py-8">
                  <DocumentChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No reports generated</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Generate your first report using the options above.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {reports.map((report) => {
                    const IconComponent = getReportIcon(report.type);
                    return (
                      <div key={report.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <IconComponent className="h-8 w-8 text-gray-400" />
                          </div>
                          <div className="ml-4">
                            <h4 className="text-sm font-medium text-gray-900">{report.title}</h4>
                            <p className="text-sm text-gray-500">
                              {report.type.charAt(0).toUpperCase() + report.type.slice(1)} • 
                              {formatDate(report.period.startDate)} - {formatDate(report.period.endDate)}
                            </p>
                            <p className="text-xs text-gray-400">
                              Generated on {formatDate(report.generatedAt)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleDownloadReport(report.id)}
                            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                          >
                            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                            Download
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CurrencyDollarIcon className="h-6 w-6 text-green-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Net Income</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(analytics.overview.netIncome)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <HomeIcon className="h-6 w-6 text-blue-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Occupancy Rate</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analytics.overview.occupancyRate.toFixed(1)}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <UserGroupIcon className="h-6 w-6 text-purple-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Tenants</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analytics.overview.totalTenants}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <WrenchScrewdriverIcon className="h-6 w-6 text-orange-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Maintenance Requests</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analytics.overview.maintenanceRequests}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts placeholder */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
            <div className="text-center py-12 text-gray-500">
              Charts and visualizations will be implemented here
            </div>
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Report Templates</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create and manage custom report templates for recurring reports.
            </p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => console.log('Create template')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;