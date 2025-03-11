import React from "react";
import pcImage from "./assets/pciamge.png";
import { BiEditAlt } from "react-icons/bi";
import { useSelector } from "react-redux";

const PCPopupWindow = ({ selectedId, mockNetworkActivity, openModal2 }) => {
  const allPCs = useSelector((state) => state.pcs.pcs)
  const selectedPC = allPCs.find((pc) => pc.id === selectedId)
  return (
    <div>
      <h1 className="text-center text-4xl font-black text-blue-500">
        {selectedId}
      </h1>
      <img src={pcImage} alt="" width="250px" className="m-auto " />
      <div className="flex justify-center items-end text-blue-500  -mt-2 mb-2">
        <h1 className="text-center text-2xl font-bold text-blue-500">
          {selectedPC.ip}
        </h1>
        <span className="text-lg pb-1 text-blue-300 hover:text-blue-500 hover:cursor-pointer">
          <BiEditAlt onClick={() => openModal2()} />
        </span>
      </div>

      <div className="flex justify-between mx-4 text-sm text-blue-500 border-b-4 border-blue-500 pb-2">
        <div className="flex">
          <p>Status : </p>
          <div className="bg-red-500 text-white px-2 pb-[2px] rounded-full justify-center ml-1">
            Unautherized
          </div>
        </div>
        <div className="flex">
          <p>Usage (Size) : </p>
          <div>45612 KB</div>
        </div>
      </div>
      <div>
        <div className="grid grid-cols-3 gap-2 text-blue-600 px-4 py-2">
          {/* Header Row */}
          <div className="font-semibold text-left col-span-2 pl-2">
            Destination IP
          </div>
          <div className="font-semibold text-right pr-4">Usage (KB)</div>
        </div>
        <div className="px-4 py-1 overflow-y-auto overflow-x-hidden h-44  ">
          {mockNetworkActivity.map((activity, index) => (
            <div
              key={index}
              className={`grid grid-cols-3 gap-2 items-center rounded-md mb-2 text-blue-500 ${
                activity.isRestricted
                  ? "border-red-200 border-1"
                  : "border-green-400 border-2"
              }`}
            >
              <div className="pl-2 py-2 col-span-2">{activity.ip}</div>
              <div className="text-right pr-2 py-2">{activity.usage}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PCPopupWindow;
