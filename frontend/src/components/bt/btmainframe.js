import React from "react";
import BkTitleName from "./bttitlename";
import BkWeather from "./btweather";

const BtMainFrame = ({ children, children2 }) => {
  return (
    <div className="whole-bk d-flex ">
      <div className="main-ml m-auto ">
        <div className="bg-white flex-column flex-container">
          <div className="flex-container flex-column" style={{ flexBasis: "30%" }}>
            <div
              className="d-flex justify-content-between mx-auto"
              style={{ flexBasis: "60%", width: "80%", height: "100%" }}>
              <div className="" style={{}}>
                <BkTitleName fontValue="28px" />
              </div>
              <div className="flex-container " style={{ flexBasis: "40%" }}>
                {/* weather Component */}
                <BkWeather></BkWeather>
              </div>
            </div>
            {children}
          </div>
          <div className="flex-container" style={{ flexBasis: "70%", position: "relative" }}>
            {children2}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BtMainFrame;
