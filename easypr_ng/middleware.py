from .models import Media_Marketing_Bundles
import cProfile, pstats, StringIO


class ProfileMiddleware(object):
	''' profiler '''
	def process_request(self, request):
		pr = cProfile.Profile()
		pr.enable()
		request._pr = pr

	def process_response(self, request, response):
		request._pr.disable()
		s = StringIO.StringIO()
		sortby = 'cumulative'
		# Sort the output by cumulative time it took in fuctions/methods.
		ps = pstats.Stats(request._pr, stream=s).sort_stats(sortby)
		# Print only 10 most time consuming functions
		ps.print_stats(20)
		print s.getvalue()
		return response
		

class MarketingBundlesMiddleware(object):
	''' collect all active marketing bundles and 
	set marketing_bundle attribute to request
	to make them visible on all pages '''
	def process_request(self, request):
		request.marketing_bundles = Media_Marketing_Bundles.objects.filter(active = True)
		return None