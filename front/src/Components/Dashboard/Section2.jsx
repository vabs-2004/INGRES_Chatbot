import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import { useState } from "react";
import OverallData from "../../assets/OverallData.js";
import "./Section2.css";

const COLORS = ["#36df0bff", "#05c4eeff", "#ff5500ff"];

export default function Section2() {
  // Default selections
  const [selectedState, setSelectedState] = useState("ARUNACHAL PRADESH");
  const [selectedDistrict, setSelectedDistrict] = useState("All");
  const [selectedYear, setSelectedYear] = useState("2024-2025");

  // Unique dropdown values
  const states = [...new Set(OverallData.map((d) => d.STATE))];
  const districts = selectedState
    ? [
        "All",
        ...new Set(
          OverallData.filter((d) => d.STATE === selectedState).map(
            (d) => d.DISTRICT
          )
        ),
      ]
    : ["All"];
  const years = [...new Set(OverallData.map((d) => d.Year))];

  // Filter by state + year
  const filteredByStateYear = OverallData.filter(
    (d) =>
      d.STATE === selectedState &&
      (selectedYear === "All" || d.Year === selectedYear)
  );

  let data = [];

  if (selectedDistrict === "All") {
    // Average across all districts
    let totalDomestic = 0,
      totalIrrigation = 0,
      totalIndustrial = 0,
      count = 0;

    filteredByStateYear.forEach((d) => {
      totalDomestic += d["Domestic"] || 0;
      totalIrrigation += d["Irrigation"] || 0;
      totalIndustrial += d["Industrial"] || 0;
      count++;
    });

    if (count > 0) {
      data = [
        { name: "Domestic", value: Math.round(totalDomestic / count) },
        { name: "Irrigation", value: Math.round(totalIrrigation / count) },
        { name: "Industrial", value: Math.round(totalIndustrial / count) },
      ];
    }
  } else {
    // Specific district
    const record = filteredByStateYear.find(
      (d) => d.DISTRICT === selectedDistrict
    );
    if (record) {
      data = [
        { name: "Domestic", value: Math.round(record["Domestic"]) || 0 },
        { name: "Irrigation", value: Math.round(record["Irrigation"]) || 0 },
        { name: "Industrial", value: Math.round(record["Industrial"]) || 0 },
      ];
    }
  }

  return (
    <div className="section2">
      <h2 style={{ marginBottom: "20px" }}>
        Section 2: Water Usage Distribution by Sector
      </h2>

      {/* Dropdown filters */}
      <div style={{ marginBottom: "20px" }}>
        <select
          value={selectedState}
          onChange={(e) => {
            setSelectedState(e.target.value);
            setSelectedDistrict("All"); // reset district on state change
          }}
        >
          {states.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          value={selectedDistrict}
          onChange={(e) => setSelectedDistrict(e.target.value)}
          style={{ marginLeft: "10px" }}
        >
          {districts.map((d) => (
            <option key={d} value={d}>
              {d}
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
        <p>No data available for the selected filters.</p>
      ) : (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <PieChart width={600} height={400}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={120}
              dataKey="value"
              labelLine={true} // draw connecting lines
              label={({ name, value }) => `${name} : ${value || 0} ham`}
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>

            {/* Dark Theme Tooltip */}
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
