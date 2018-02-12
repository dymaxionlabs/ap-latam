module.exports = {
  siteMetadata: {
    name: 'VyA Latam',
    title: 'Mapa de potenciales villas y asentamientos'
  },
  plugins: [
    'gatsby-plugin-react-helmet',
    'gatsby-plugin-sass',
    {
      resolve: 'gatsby-source-filesystem',
      options: {
        name: 'data',
        path: `${__dirname}/data/`,
      },
    },
    'gatsby-transformer-json'
  ],
};
