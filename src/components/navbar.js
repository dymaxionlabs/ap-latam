import React from 'react'
import Link from 'gatsby-link'

const NavBar = props => (
  <nav className="navbar" role="navigation" aria-label="main pagination">
    <div className="navbar-brand">
      <Link to="/">{props.name}</Link>

      <button className="button navbar-burger" data-target="navMenu">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

    <div className="navbar-menu" id="navMenu">
      <div className="navbar-end">
        <a className="navbar-item">
          <Link to="/map">Mapa</Link>
        </a>
        <a className="navbar-item">
          <Link to="/data">Datos</Link>
        </a>
        <a className="navbar-item">
          <Link to="/publications">Publicaciones</Link>
        </a>
        <a className="navbar-item">
          <Link to="/license">Licencia</Link>
        </a>
        <a className="navbar-item">
          <Link to="/contact">Contacto</Link>
        </a>
      </div>
    </div>
  </nav>
)

export default NavBar

document.addEventListener('DOMContentLoaded', () => {
  // Get all "navbar-burger" elements
  let $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {
    // Add a click event on each of them
    $navbarBurgers.forEach(function ($el) {
      $el.addEventListener('click', function () {
        // Get the target from the "data-target" attribute
        let target = $el.dataset.target;
        let $target = document.getElementById(target);

        // Toggle the class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');
      });
    });
  }
});
