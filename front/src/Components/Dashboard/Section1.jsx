import React, { useState, useEffect } from "react";
import "./Section1.css";
import OverallData from "../../assets/OverallDataSection1.js";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const Section1 = () => {
  const defaultState = "ARUNACHAL PRADESH";

  const [selectedState, setSelectedState] = useState(defaultState);
  const [selectedDistrict, setSelectedDistrict] = useState("All");

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

  const filteredByState = OverallData.filter((d) => d.STATE === selectedState);

  let chartData = [];

  if (selectedDistrict === "All") {
    // Average across all districts for each year
    const groupedByYear = {};

    filteredByState.forEach((d) => {
      const year = d.Year;
      if (!groupedByYear[year])
        groupedByYear[year] = {
          annualRecharge: 0,
          freshWaterAvailability: 0,
          count: 0,
        };

      groupedByYear[year].annualRecharge +=
        d["Annual Ground water Recharge (ham) Total"];
      groupedByYear[year].freshWaterAvailability +=
        d["Total Ground Fresh Water Availability in the area (ham)"];
      groupedByYear[year].count += 1;
    });

    chartData = Object.entries(groupedByYear).map(([year, values]) => ({
      year,
      annualRecharge: Math.round(values.annualRecharge / values.count),
      freshWaterAvailability: Math.round(values.freshWaterAvailability / values.count),
    }));
  } else {
    
    chartData = filteredByState
      .filter((d) => d.DISTRICT === selectedDistrict)
      .map((d) => ({
        year: d.Year,
        annualRecharge: Math.round(d["Annual Ground water Recharge (ham) Total"]),
        freshWaterAvailability:
          Math.round(d["Total Ground Fresh Water Availability in the area (ham)"]),
      }));
  }

  chartData.sort(
    (a, b) => parseInt(a.year.split("-")[0]) - parseInt(b.year.split("-")[0])
  );

  useEffect(() => {
    setSelectedDistrict("All");
  }, [selectedState]);

  return (
    <div
      className="section1"
      style={{ padding: "20px", borderBottom: "1px solid #ccc" }}
    >
      <h2>Section 1: Annual Ground Water Recharge vs Availability</h2>
      {/* Dropdown filters */}
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
      </div>

      {/* Line Chart */}
      <LineChart
        width={1100}
        height={300}
        data={chartData}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid stroke="#444" strokeDasharray="3 3" />
        <XAxis dataKey="year" stroke="#fff" />
        <YAxis stroke="#fff" />
        <Tooltip
          formatter={(value, name) => [`${value} ham`, name]} 
          contentStyle={{
            backgroundColor: "#2a2a40",
            border: "1px solid #555",
            color: "#fff",
          }}
        />
        <Legend wrapperStyle={{ color: "#fff" }} />
        <Line
          type="monotone"
          dataKey="annualRecharge"
          stroke="#ff6b6b" 
          strokeWidth={2}
          name="Annual Ground Water Recharge"
        />
        <Line
          type="monotone"
          dataKey="freshWaterAvailability"
          stroke="#4ecdc4" 
          strokeWidth={2}
          name="Fresh Ground Water Availability"
        />
      </LineChart>
    </div>
  );
};

export default Section1;
