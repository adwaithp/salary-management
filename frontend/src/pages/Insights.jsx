import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";
import { getOverview, getCountrySummary, getDepartmentSummary, getTopEarners } from "../api/insights";
import { Users, TrendingUp, TrendingDown, DollarSign, Loader2 } from "lucide-react";

const fmt = (n) => `$${Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
const COLORS = ["#3b82f6","#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981","#06b6d4","#ef4444","#84cc16","#f97316"];

function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500 font-medium">{label}</p>
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon size={16} className="text-white" />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function SectionTitle({ children }) {
  return <h2 className="text-base font-semibold text-gray-900 mb-4">{children}</h2>;
}

function ChartCard({ title, children, loading }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <SectionTitle>{title}</SectionTitle>
      {loading ? (
        <div className="flex items-center justify-center h-52">
          <Loader2 size={22} className="animate-spin text-blue-500" />
        </div>
      ) : children}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg">
      <p className="font-medium mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name}>{p.name}: {fmt(p.value)}</p>
      ))}
    </div>
  );
};

export default function Insights() {
  const { data: overview, isLoading: ovLoading } = useQuery({ queryKey: ["overview"], queryFn: getOverview });
  const { data: countries = [], isLoading: cLoading } = useQuery({ queryKey: ["country-summary"], queryFn: getCountrySummary });
  const { data: departments = [], isLoading: dLoading } = useQuery({ queryKey: ["dept-summary"], queryFn: getDepartmentSummary });
  const { data: topEarners = [], isLoading: tLoading } = useQuery({ queryKey: ["top-earners"], queryFn: () => getTopEarners(10) });

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Salary Insights</h1>
        <p className="text-gray-500 text-sm mt-0.5">Organisation-wide salary analytics</p>
      </div>

      {/* Stat cards */}
      {ovLoading ? (
        <div className="flex items-center justify-center h-24">
          <Loader2 size={22} className="animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Employees" value={overview?.total_employees?.toLocaleString() ?? "—"} icon={Users}       color="bg-blue-500" />
          <StatCard label="Average Salary"  value={overview ? fmt(overview.avg_salary)  : "—"} icon={TrendingUp}  color="bg-green-500" />
          <StatCard label="Highest Salary"  value={overview ? fmt(overview.max_salary)  : "—"} icon={DollarSign}  color="bg-purple-500" />
          <StatCard label="Lowest Salary"   value={overview ? fmt(overview.min_salary)  : "—"} icon={TrendingDown} color="bg-orange-500" />
        </div>
      )}

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Avg salary by country */}
        <ChartCard title="Average Salary by Country" loading={cLoading}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={countries} margin={{ top: 4, right: 4, left: 10, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="country" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_salary" name="Avg Salary" radius={[4,4,0,0]}>
                {countries.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Avg salary by department */}
        <ChartCard title="Average Salary by Department" loading={dLoading}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={departments} margin={{ top: 4, right: 4, left: 10, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="department" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_salary" name="Avg Salary" radius={[4,4,0,0]}>
                {departments.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Country detail table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <SectionTitle>Salary Range by Country</SectionTitle>
          {cLoading ? <Loader2 size={20} className="animate-spin text-blue-500" /> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {["Country", "Headcount", "Min", "Max", "Avg"].map((h) => (
                    <th key={h} className="text-left py-2 text-xs font-semibold text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {countries.map((r) => (
                  <tr key={r.country} className="hover:bg-gray-50">
                    <td className="py-2.5 font-medium text-gray-900">{r.country}</td>
                    <td className="py-2.5 text-gray-500">{r.headcount.toLocaleString()}</td>
                    <td className="py-2.5 text-gray-600">{fmt(r.min_salary)}</td>
                    <td className="py-2.5 text-gray-600">{fmt(r.max_salary)}</td>
                    <td className="py-2.5 font-medium text-blue-600">{fmt(r.avg_salary)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Top earners */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <SectionTitle>Top 10 Earners</SectionTitle>
          {tLoading ? <Loader2 size={20} className="animate-spin text-blue-500" /> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {["#", "Name", "Job Title", "Salary"].map((h) => (
                    <th key={h} className="text-left py-2 text-xs font-semibold text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {topEarners.map((emp, i) => (
                  <tr key={emp.id} className="hover:bg-gray-50">
                    <td className="py-2.5 text-gray-400 font-medium">{i + 1}</td>
                    <td className="py-2.5 font-medium text-gray-900">{emp.full_name}</td>
                    <td className="py-2.5 text-gray-500 text-xs">{emp.job_title}</td>
                    <td className="py-2.5 font-semibold text-green-600">{fmt(emp.salary)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
