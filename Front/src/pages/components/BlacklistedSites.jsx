export default function BlacklistedSites({ sites }) {
  return (
    <div className="p-2 border-2 border-blue-500 rounded-lg">
      <h2 className="font-bold text-center text-lg text-blue-500">Blacklisted Sites</h2>
      <ul>
        {sites.map((site, index) => (
          <li
            key={index}
            className="p-2 bg-blue-400 rounded-md my-1 text-blue-900 flex justify-between"
          >
            <span>{site.name}</span>

            <span className="bg-blue-900 text-white px-2 rounded-full">
              {site.count}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
