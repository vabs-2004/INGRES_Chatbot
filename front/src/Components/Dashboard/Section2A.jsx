import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";
import { useState } from "react";
import OverallData from "../../assets/OverallData.js";
import './Section2A.css';

const COLORS = ["#36df0bff", "#05c4eeff", "#ff5500ff", "#f8d210", "#a020f0"];

export default function Section2A() {
  const [selectedState, setSelectedState] = useState("ARUNACHAL PRADESH");
  const [selectedYear, setSelectedYear] = useState("2024-2025");

  const states = [...new Set(OverallData.map((d) => d.STATE))];
  const years = [...new Set(OverallData.map((d) => d.Year))];

  const filteredData = OverallData.filter(
    (d) => d.STATE === selectedState && d.Year === selectedYear
  );

  // Prepare rainfall data per district
  let data = filteredData.map((d) => ({
    name: d.DISTRICT,
    value: Math.round(d["Rainfall(mm) Total"]) || 0,
  }));

  // Sort districts by rainfall descending and pick top 5 if more than 5
  data.sort((a, b) => b.value - a.value);
  if (data.length > 5) {
    data = data.slice(0, 5);
  }

  return (
    <div className="section2A">
      <h2 style={{ marginBottom: "20px" }}>
       Section 3: Rainfall Distribution - {selectedState} ({selectedYear})
      </h2>

      {/* Dropdowns */}
      <div style={{ marginBottom: "20px" }}>
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
        >
          {states.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target.value)}
          style={{ marginLeft: "10px" }}
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Pie Chart */}
      {data.length === 0 ? (
        <p>No rainfall data available for the selected filters.</p>
      ) : (
        <div style={{ display: "flex", justifyContent: "center" , alignItems: "center"}}>
          <PieChart width={800} height={400}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={150}
              dataKey="value"
              label={({ name, value }) => `${name}: ${value} ham`}
              stroke="none" 
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
             <Tooltip
              formatter={(value, name) => [`${value} ham`, name]} // add ham unit
              contentStyle={{
                backgroundColor: "#2c2c3e",
                border: "1px solid #555",
                borderRadius: "8px",
                color: "#fff",
                boxShadow: "0 4px 10px rgba(0,0,0,0.4)",
              }}
              itemStyle={{
                color: "#fff",
              }}
              labelStyle={{
                color: "#aaa",
              }}
            />
            <Legend />
          </PieChart>
        </div>
      )}
    </div>
  );
}
