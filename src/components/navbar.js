import React from 'react'
import Link from 'gatsby-link'

const NavBarBurger = props => {
  const activeClass = props.active ? 'is-active' : ''
  const classes = `button navbar-burger ${activeClass}`
  return (
    <button className={classes} onClick={props.handler}>
      <span></span>
      <span></span>
      <span></span>
    </button>
  )
}

const NavBarMenu = props => {
  const activeClass = props.active ? 'is-active' : ''
  const classes = `navbar-menu ${activeClass}`
  return (
    <div className={classes} id="navMenu">
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
  )
}

class NavBar extends React.Component {
  constructor(props) {
    super(props)
    this.state = {active: false}
    this.toggleActive = this.toggleActive.bind(this)
  }

  toggleActive() {
    this.setState((prevState, props) => ({active: !prevState.active}))
    console.log(`toggle active: ${this.state.active}`)
  }

  render() {
    return (
      <nav className="navbar" role="navigation" aria-label="main pagination">
        <div className="navbar-brand">
          <Link to="/">{this.props.name}</Link>
          <NavBarBurger active={this.state.active} handler={this.toggleActive} />
        </div>
        <NavBarMenu active={this.state.active} />
      </nav>
    )
  }
}

export default NavBar
