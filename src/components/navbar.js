import React from 'react'
import Link from 'gatsby-link'

const NavBarBurger = props => {
  const activeClass = props.active ? 'is-active' : ''
  const classes = `button navbar-burger ${activeClass}`
  return (
    <button className={classes} onClick={props.handler}>
      <span />
      <span />
      <span />
    </button>
  )
}

const NavBarMenu = props => {
  const activeClass = props.active ? 'is-active' : ''
  const classes = `navbar-menu ${activeClass}`
  return (
    <div className={classes} id="navMenu">
      <div className="navbar-end">
        <Link className="navbar-item" to="/map">
          Mapa
        </Link>
        <Link className="navbar-item" to="/data">
          Datos
        </Link>
        <Link className="navbar-item" to="/publications">
          Publicaciones
        </Link>
        <Link className="navbar-item" to="/license">
          Licencia
        </Link>
        <Link className="navbar-item" to="/contact">
          Contacto
        </Link>
      </div>
    </div>
  )
}

class NavBar extends React.Component {
  constructor(props) {
    super(props)
    this.state = { active: false }
    this.toggleActive = this.toggleActive.bind(this)
  }

  toggleActive() {
    this.setState((prevState, props) => ({ active: !prevState.active }))
  }

  render() {
    return (
      <nav className="navbar" role="navigation" aria-label="main pagination">
        <div className="navbar-brand">
          <Link style={{ fontWeight: 500 }} className="navbar-item" to="/">
            {this.props.name}
          </Link>
          <NavBarBurger
            active={this.state.active}
            handler={this.toggleActive}
          />
        </div>
        <NavBarMenu active={this.state.active} />
      </nav>
    )
  }
}

export default NavBar
