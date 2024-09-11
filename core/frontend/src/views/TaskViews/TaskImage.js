import React, { Component } from "react";

import {
  TransformWrapper,
  TransformComponent,
  useControls,
} from "react-zoom-pan-pinch";

const Controls = () => {
  const { zoomIn, zoomOut, resetTransform, centerView } = useControls();

  return (
    <div className="tools">
      <button onClick={() => zoomIn()}>Zoom In +</button>
      <button onClick={() => zoomOut()}>Zoom Out -</button>
      <button onClick={() => resetTransform()}>Reset</button>
      <button onClick={() => centerView()}>Center</button>
    </div>
  );
};

const TaskImage = ({ imageUrl }) => {
  return (
    <TransformWrapper
      initialScale={2}
      centerOnInit
    >
      {({ zoomIn, zoomOut, resetTransform, centerView, ...rest }) => (
        <React.Fragment>
          <TransformComponent>
            <img src={imageUrl} alt="task image" style={{ width: '100%', height: '100%' }}/>
          </TransformComponent>
          <Controls />
        </React.Fragment>
      )}
    </TransformWrapper>
  );
};
export default TaskImage;

// import { Image } from 'semantic-ui-react';

// const TaskImage = ({ imageUrl }) => {
//   return (
//     <Image src={imageUrl} centered />
//   );
// };

// export default TaskImage;

