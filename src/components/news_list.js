import React from 'react'

const NewsList = props => (
  <table className="table is-fullwidth">
    {props.items.map(item => <NewsListItem key={item.url} item={item} />)}
  </table>
)

const NewsListItem = props => (
  <tr>
    <th>{props.item.name}</th>
    <td>
      <a href={props.item.url} target="_blank">
        {props.item.title}
      </a>
    </td>
  </tr>
)

export default { NewsList, NewsListItem }
