import React, { useState } from "react";
import "./Section3.css";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
} from "recharts";
import OverallData from "../../assets/OverallData.js";

export default function Section3() {
  const defaultState = "ARUNACHAL PRADESH";
  const defaultYear = "2024-2025";

  const [selectedYear, setSelectedYear] = useState(defaultYear);
  const [selectedState, setSelectedState] = useState(defaultState);

  const years = [...new Set(OverallData.map((d) => d.Year))];
  const states = [...new Set(OverallData.map((d) => d.STATE))];

  const filtered =
    selectedYear && selectedState
      ? OverallData.filter(
          (d) => d.Year === selectedYear && d.STATE === selectedState
        )
      : [];

  // Keep percentage as number (not string!)
  const districtData = filtered
    .map((d) => ({
      district: d.DISTRICT,
      percentage: parseFloat(d["Stage of Ground Water Extraction (%) Total"]),
    }))
    .sort((a, b) => b.percentage - a.percentage);

  // If more than 10 districts, take top 10
  const displayedDistrictData =
    districtData.length > 10 ? districtData.slice(0, 10) : districtData;

  const showTopNote = districtData.length > 10;

  // Function to assign colors based on category
  const getBarColor = (value) => {
    if (value > 100) return "#ff1818"; // Over-Exploited
    if (value > 90) return "#ff7e67"; // Critical
    if (value > 70) return "#FFA500"; // Semi-Critical
    return "#00C49F"; // Safe
  };

  return (
    <div className="section3">
      <h2>District-wise Groundwater Extraction (%)</h2>

      <div className="dropdowns">
        <div>
          <label>Select State: </label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
          >
            {states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Select Year: </label>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>

      {showTopNote && (
        <p style={{ fontStyle: "italic", color: "#888", marginTop: "5px" }}>
          Showing top 10 districts with highest groundwater extraction
        </p>
      )}

      <ResponsiveContainer width="95%" height={490}>
        <BarChart data={displayedDistrictData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <YAxis
            type="category"
            dataKey="district"
            width={150}
            tick={{ fontSize: 12, fill: "#fff" }} // White text for Y-axis
          />
          <XAxis type="number" tick={{ fill: "#fff" }} />{" "}
          {/* White X-axis text */}
          <Tooltip
            contentStyle={{
              backgroundColor: "#222",
              border: "1px solid #555",
              borderRadius: "8px",
              padding: "8px",
            }}
            itemStyle={{ color: "#fff", fontSize: 14 }}
            formatter={(value, name) => [`${value.toFixed(2)}%`, name]}
          />
          <Bar dataKey="percentage">
            {displayedDistrictData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBarColor(entry.percentage)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Custom legend */}
      <div style={{ marginTop: "10px", fontSize: "14px" }}>
        <span style={{ color: "#00C49F" }}>■ Safe (≤70%) </span>
        <span style={{ color: "#FFA500", marginLeft: "10px" }}>
          ■ Semi-Critical (70–90%)
        </span>
        <span style={{ color: "#ff7e67", marginLeft: "10px" }}>
          ■ Critical (90–100%)
        </span>
        <span style={{ color: "#ff1818", marginLeft: "10px" }}>
          ■ Over-Exploited (&gt;100%)
        </span>
      </div>
    </div>
  );
}
