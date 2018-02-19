import React from 'react'
import Link from 'gatsby-link'

const LanguageSelector = props => {
  const langNames = {
    'en': 'English',
    'es': 'Español'
  }
  return (
    <div className="navbar-item has-dropdown is-hoverable">
      <a className="navbar-link">
        {langNames[props.lang]}
      </a>
      <div className="navbar-dropdown">
        {Object.entries(langNames).map(lang => {
          const href = `/${lang[0]}`
          return (
            <a key={lang[0]} href={href} className="navbar-item">{lang[1]}</a>
          )
        })}
      </div>
    </div>
  )
}

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

const NavBarItem = props => (
  <Link className="navbar-item" to={props.url}>{props.name}</Link>
)

const NavBarMenu = props => {
  const activeClass = props.active ? 'is-active' : ''
  const classes = `navbar-menu ${activeClass}`
  return (
    <div className={classes} id="navMenu">
      <div className="navbar-end">
        {props.children}
        <hr className="navbar-divider" />
        <LanguageSelector lang={props.lang} />
      </div>
    </div>
  )
}

class NavBar extends React.Component {
  constructor(props) {
    super(props)
    this.state = { active: false }
    this.toggleActive = this.toggleActive.bind(this)
    this.lang = this.props.prefix.slice(1)
  }

  toggleActive() {
    this.setState((prevState, props) => ({ active: !prevState.active }))
  }

  render() {
    return (
      <nav className="navbar" role="navigation" aria-label="main pagination">
        <div className="navbar-brand">
          <Link style={{ fontWeight: 500 }} className="navbar-item" to={this.props.prefix}>
            {this.props.name}
          </Link>
          <NavBarBurger
            active={this.state.active}
            handler={this.toggleActive}
          />
        </div>
        <NavBarMenu active={this.state.active} lang={this.lang}>
          {this.props.children}
        </NavBarMenu>
      </nav>
    )
  }
}

export default {NavBar, NavBarItem}
