import React from "react";
import PCItem from "./PCItem";

const PCsStatus = ({
  mockPCs,
  mockNetworkActivity,
  mockHighBandwidth,
  selectedLab,
  filteredPCs,
  noOfRows,
  setClicked
}) => {
  const renderPCsGrid = (pcs) => {
    if (selectedLab === "All") {
      const groupedPCs = [
        pcs.slice(0, 25),
        pcs.slice(25, 50),
        pcs.slice(50, 75),
        pcs.slice(75, 100),
      ];

      return (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)" }}>
          {groupedPCs.map((group, index) => (
            <div key={index} className="mx-3 mb-2">
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: `repeat(5, 1fr)`,
                  gap: "5px",
                }}
              >
                {group.map((pc) => (
                  <PCItem pc={pc} setClicked={setClicked} />
                ))}
              </div>
            </div>
          ))}
        </div>
      );
    } else if (selectedLab === "CSL3" || selectedLab === "CSL4") {
      const groupedPCs = [
        pcs.slice(0, 25),
        pcs.slice(25, 50),
        pcs.slice(50, 75),
        pcs.slice(75, 100),
      ];

      return (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)" }}>
          {groupedPCs.map((group, index) => (
            <div key={index} className="mx-3 mb-2">
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: `repeat(5, 1fr)`,
                  gap: "5px",
                }}
              >
                {group.map((pc) => (
                  <PCItem pc={pc} setClicked={setClicked} />
                ))}
              </div>
            </div>
          ))}
        </div>
      );
    }

    const rows = [];
    for (let i = 0; i < pcs.length; i += 5) {
      rows.push(pcs.slice(i, i + 5));
    }

    return rows.map((row, rowIndex) => (
      <div
        key={rowIndex}
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${noOfRows * 5}, 1fr)`,
          gap: "5px",
          marginTop: "10px",
        }}
      >
        {row.map((pc) => (
          <PCItem pc={pc} setClicked={setClicked} />
        ))}
      </div>
    ));
  };

  return (
    <div className="border-2 border-blue-400 w-full rounded-lg">
      <div className="text-center">
        <h2 className="text-lg font-bold text-blue-500">PC Status</h2>
        {renderPCsGrid(filteredPCs)}
      </div>
    </div>
  );
};

export default PCsStatus;
