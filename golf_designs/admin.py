from django.contrib import admin
from golf_designs.models import User, Citation, SubmissionInfo, GolfInstance, GolfInstanceUpperBound, GolfSolution

admin.site.register(User)
admin.site.register(Citation)
admin.site.register(SubmissionInfo)
admin.site.register(GolfInstance)
admin.site.register(GolfInstanceUpperBound)
admin.site.register(GolfSolution)

