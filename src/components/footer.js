import React from 'react'

const Footer = ({ children }) => (
  <footer className="footer">
    <div className="container">
      <div className="content has-text-centered">
        <p>{children}</p>
      </div>
    </div>
  </footer>
)

export default Footer
