import React from "react";
import { useSelector } from "react-redux";

export default function BlacklistedSites({ sites }) {
  const blacklistedIPs = useSelector((state) => state.blacklist.blackListedIPs);

  return (
    <div className="p-2 border-2 border-blue-500 rounded-lg">
      <h2 className="font-bold text-center text-lg text-blue-500">
        Blacklisted Sites
      </h2>
      <ul>
        {/* {sites.map((site, index) => (
          <li
            key={index}
            className="p-2 bg-blue-400 rounded-md my-1 text-blue-900 flex justify-between"
          >
            <span>{site.name}</span>

            <span className="bg-blue-900 text-white px-2 rounded-full">
              {site.count}
            </span>
          </li>
        ))} */}
        {blacklistedIPs.length > 0 ? (
          blacklistedIPs.map((ip, index) => (
            <li
              key={index}
              className="p-2 bg-blue-400 rounded-md my-1 text-blue-900 flex justify-between"
            >
              {/* <strong>Name:</strong> {ip.name}, <strong>IP:</strong> {ip.ip}, <strong>DNS:</strong> {ip.dns}, <strong>Restriction:</strong> {ip.restrictionType} */}
              <span>{ip.name}</span>

              <span className="bg-blue-900 text-white px-2 rounded-full">
                {/* {ip.count} */}#
              </span>
            </li>
          ))
        ) : (
          <p>No IPs blacklisted yet.</p>
        )}
      </ul>
    </div>
  );
}
