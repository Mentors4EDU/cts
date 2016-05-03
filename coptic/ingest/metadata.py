import logging
import requests
from bs4 import BeautifulSoup
from texts.models import TextMeta, CorpusMeta

logger = logging.getLogger(__name__)


def collect_corpus_meta(url, corpus):
	logger.info("Fetching and saving corpus metadata")
	def factory(): return CorpusMeta()
	collect(url, factory, corpus.corpus_meta)


def collect_text_meta(url, text):
	logger.info("Fetching and saving text metadata")
	def factory(): return TextMeta()
	collect(url, factory, text.text_meta)


def collect(url, factory, parent):
	parent.remove()
	for fields in get_selected_annotation_fields(url, ('name', 'value', 'pre', 'corpusname')):
		meta = factory()
		meta.name, meta.value, meta.pre, meta.corpus_name = fields
		meta.save()
		parent.add(meta)


def get_selected_annotation_fields(url, field_names):
	'Fetch from the url, and return the requested fields for each annotation found, in a list of lists'
	try:
		response = requests.get(url)
		content = response.content
		soup = BeautifulSoup(content)
		annotations = soup.find_all("annotation")
		annotation_sets = [[a.find(n).text for n in field_names] for a in annotations]
		logger.info('Got %d annotation sets from %s' % (len(annotation_sets), url))
		if url == 'https://corpling.uis.georgetown.edu/annis-service/annis/meta/doc/apophthegmata.patrum/AP.005.unid.senses':
			logger.info(content)
			ce = [aset[1] for aset in annotation_sets if aset[0] == 'Coptic_edition'][0]
			logger.info('Edition: %s' % ce)

		return annotation_sets
	except Exception as e:
		logger.exception(e)
		return []
