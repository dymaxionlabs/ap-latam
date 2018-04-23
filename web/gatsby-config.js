const languages = require('./src/data/languages')
const press = require('./src/data/press')

module.exports = {
  pathPrefix: '/ap-latam',
  siteMetadata: {
    name: 'AP Latam',
    title: 'Monitor de potenciales asentamientos informales y barrios precarios',
    meta: {
      description: 'El mapa está elaborado a partir de la aplicación de técnicas de machine learning en imágenes satelitales y otros datos georreferenciados.'
    },
    languages,
    press
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
    'gatsby-transformer-json',
    {
      resolve: `gatsby-plugin-google-analytics`,
      options: {
        trackingId: 'UA-105156301-3',
        head: true,
        anonymize: true,
      },
    },
    {
      resolve: 'gatsby-plugin-i18n',
      options: {
        langKeyForNull: 'any',
        langKeyDefault: 'es',
        useLangKeyLayout: true
      }
    }
  ],
};
