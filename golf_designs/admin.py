from django.contrib import admin
from golf_designs.models import User, Citation, SubmissionInfo, GolfInstance, GolfUpperBound, GolfSolution

admin.site.register(User)
admin.site.register(Citation)
admin.site.register(SubmissionInfo)
admin.site.register(GolfInstance)
admin.site.register(GolfUpperBound)
admin.site.register(GolfSolution)

