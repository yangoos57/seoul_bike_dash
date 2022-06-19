import React from "react";
import "./assets/mlstyle.css";
import MlMap from "./mlmap";
import MlTitle from "./mltitle";
import MlSearchPage from "./mlsearchpage";
function MLMain() {
  return (
    <>
      <div className="whole-ml">
        <div className="main-ml m-auto ">
          {/* <MlTitle /> */}
          {/* <MlMap /> */}
          <MlSearchPage />
        </div>
      </div>
    </>
  );
}
export default MLMain;
