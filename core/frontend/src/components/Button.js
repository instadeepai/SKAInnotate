import React from 'react';
import '../assets/styles/Button.css';

const Button = ({ type = 'primary', children, ...props }) => {
  const className = `button button-${type}`;
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
};

export default Button;
