import React from 'react'
import Footer from './_footer.es'

const PublicationsEsPage = () => (
  <div>
    <section className="section">
      <div className="container">
        <h1 className="title">Publicaciones</h1>
        <div className="content">
          <ul className="list">
            <li>
              <p>
                <a
                  href="http://digital.bl.fcen.uba.ar/gsdl-282/cgi-bin/library.cgi?a=d&c=tesis&d=Tesis_6172_Bayle"
                  target="_blank"
                >
                  Detección de villas y asentamientos informales en el partido
                  de La Matanza mediante teledetección y sistemas de información
                  geográfica
                </a>
              </p>
              <p>
                Realizar un relevamiento de campo requiere contar con recursos
                logísticos para poder hacerlo de manera exhaustiva. La creciente
                disponibilidad de datos abiertos, imágenes satelitales de alta
                resolución y software libre para procesarlos abre la puerta a
                poder hacerlo de manera escalable a partir del análisis de esas
                fuentes de información. En el presente trabajo se hizo un
                ejercicio de ese tipo para detectar villas y asentamientos en el
                Partido de La Matanza considerando el relevamiento realizado por
                la ONG Techo en 2013. El objetivo es proponer una metodología
                que reduzca el área del territorio a relevar, teniendo en cuenta
                la periodicidad y actualización de los conjuntos de datos. Se
                utilizaron datos censales, viales y naturales georreferenciados,
                imágenes satelitales y algoritmos de aprendizaje automático. Los
                resultados muestran que usando la metodología propuesta con
                todas las fuentes de datos mencionadas se logra reducir el
                territorio a un 16% (51km2), mientras que considerando solamente
                imágenes se reduce a 30% (96km2).
              </p>
            </li>
          </ul>
        </div>
      </div>
    </section>
    <Footer />
  </div>
)

export default PublicationsEsPage
