from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class IndoorSchematic(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('pontoportas', 'pontoPortas', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('vetorcorredor', 'vetorCorredor', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultado', 'resultado', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(14, model_feedback)
        results = {}
        outputs = {}

        # Buffer
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 1,
            'END_CAP_STYLE': 0,
            'INPUT': parameters['vetorcorredor'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Densificar por intervalo
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'INTERVAL': 0.1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DensificarPorIntervalo'] = processing.run('native:densifygeometriesgivenaninterval', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extrair vértices
        alg_params = {
            'INPUT': outputs['DensificarPorIntervalo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairVrtices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Polígonos de Voronoi
        alg_params = {
            'BUFFER': 100,
            'INPUT': outputs['ExtrairVrtices']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolgonosDeVoronoi'] = processing.run('qgis:voronoipolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Polígonos para linhas
        alg_params = {
            'INPUT': outputs['PolgonosDeVoronoi']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolgonosParaLinhas'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Explodir linhas
        alg_params = {
            'INPUT': outputs['PolgonosParaLinhas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExplodirLinhas'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Selecionar por localização
        alg_params = {
            'INPUT': outputs['ExplodirLinhas']['OUTPUT'],
            'INTERSECT': parameters['vetorcorredor'],
            'METHOD': 0,
            'PREDICATE': 6
        }
        outputs['SelecionarPorLocalizao'] = processing.run('native:selectbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extrair feições selecionadas
        alg_params = {
            'INPUT': outputs['ExplodirLinhas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairFeiesSelecionadas'] = processing.run('native:saveselectedfeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Dissolver
        alg_params = {
            'FIELD': None,
            'INPUT': outputs['ExtrairFeiesSelecionadas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolver'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Simplificar
        alg_params = {
            'INPUT': outputs['Dissolver']['OUTPUT'],
            'METHOD': 0,
            'TOLERANCE': 0.01,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Simplificar'] = processing.run('native:simplifygeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Densificar por intervalo
        alg_params = {
            'INPUT': outputs['Simplificar']['OUTPUT'],
            'INTERVAL': 0.1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DensificarPorIntervalo'] = processing.run('native:densifygeometriesgivenaninterval', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extrair vértices
        alg_params = {
            'INPUT': outputs['DensificarPorIntervalo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairVrtices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Distância para o ponto central mais próximo (linha para ponto central)
        alg_params = {
            'FIELD': 'fid',
            'HUBS': outputs['ExtrairVrtices']['OUTPUT'],
            'INPUT': parameters['pontoportas'],
            'UNIT': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistnciaParaOPontoCentralMaisPrximoLinhaParaPontoCentral'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # União
        alg_params = {
            'INPUT': outputs['DistnciaParaOPontoCentralMaisPrximoLinhaParaPontoCentral']['OUTPUT'],
            'OVERLAY': outputs['Simplificar']['OUTPUT'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': parameters['Resultado']
        }
        outputs['Unio'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultado'] = outputs['Unio']['OUTPUT']
        return results

    def name(self):
        return 'Indoor Schematic'

    def displayName(self):
        return 'Indoor Schematic'


    def createInstance(self):
        return IndoorSchematic()
