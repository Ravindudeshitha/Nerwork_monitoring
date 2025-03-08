import pcImage from "./assets/pciamge.png";

export default function PCItem({ pc, setClicked }) {
  const getBorderColor = () => {
    switch (pc.status) {
      case "restricted":
        return "border-red-500";
      case "active":
        return "border-green-400";
      default:
        return "border-gray-400";
    }
  };

  const getLabelColor = () => {
    switch (pc.status) {
      case "restricted":
        return "bg-red-500";
      case "active":
        return "bg-green-400";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div
      className={`border-4 hover:cursor-pointer ${getBorderColor()} p-1 rounded-md ${
        pc.status === "disconnected" ? "opacity-50" : "opacity-100"
      }`}
      onClick={() => setClicked(pc.id)}
    >
      <div
        className={`absolute ${getLabelColor()} px-[2px] rounded-br-md rounded-tl-md`}
      >
        {pc.id}
      </div>
      <img src={pcImage} alt="" />
    </div>
  );
}
