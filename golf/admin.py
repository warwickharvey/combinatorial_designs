from django.contrib import admin
from golf.models import User, Citation, SubmissionInfo, GolfInstance, GolfUpperBound, GolfLowerBound, GolfSolution

admin.site.register(User)
admin.site.register(Citation)
admin.site.register(SubmissionInfo)
admin.site.register(GolfInstance)
admin.site.register(GolfUpperBound)
admin.site.register(GolfLowerBound)
admin.site.register(GolfSolution)

