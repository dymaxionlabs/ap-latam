module.exports = {
  pathPrefix: '/ap-latam',
  siteMetadata: {
    name: 'AP Latam',
    title: 'Mapa de potenciales asentamientos informales y barrios precarios',
    press: [{
      name: "La Nación",
      title: "Desarrollan un mapa online que permite monitorear el crecimiento de las villas en la Argentina",
      url: "http://www.lanacion.com.ar/2057737-desarrollan-un-mapa-online-que-permite-monitorear-el-crecimiento-de-las-villas-en-la-argentina"
    }, {
      name: "C5N",
      title: "Crearon un mapa que permite monitorear el crecimiento de las villas",
      url: "https://www.youtube.com/watch?v=gIcPSnNyxVs"
    }, {
      name: "La Gaceta",
      title: "Mapa interactivo: mirá en qué lugares crecieron las villas en los últimos años",
      url: "http://www.lagacetasalta.com.ar/nota/88432/actualidad/mapa-interactivo-mira-lugares-crecieron-villas-ultimos-anos.html"
    }, {
        name: "Radio",
        title: "Inventos Argentinos: Dymaxion Labs y detección de asentamientos informales a gran escala",
        url: "https://radiocut.fm/audiocut/inventos-argentinos-dymaxion-labs-y-deteccion-de-asentamientos-informales-a-gran-escala/"
    }]
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
        trackingId: 'UA-99996075-1',
        head: false,
        anonymize: true,
      },
    },
  ],
};
