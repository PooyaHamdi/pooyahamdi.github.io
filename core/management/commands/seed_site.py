"""Load starting content.

Scholar numbers and publications are from the public Scholar profile; bio,
contact, education, career and projects are from the RWTH staff page
(both read Nov 2026). Entries marked TODO are placeholders to replace in the admin.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Education, Experience, Profile, Project, Publication, ScholarStats, Student

SCHOLAR_URL = "https://scholar.google.com/citations?user=QqegjnAAAAAJ&hl=en"
RWTH_URL = "https://www.lih.rwth-aachen.de/cms/lih/der-lehrstuhl/team/ingenieurgeologie/~rvvd/pooya-hamdi/?allou=1&lidx=1"
LIH = "https://www.lih.rwth-aachen.de"

BIO = """\
I am a Senior Scientist and Leader of the Rock Mechanics Group at the Chair of Engineering Geology and Hydrogeology, RWTH Aachen University. My research focuses on rock mechanics, rock engineering design and numerical modelling, applied to rock slope and landslide analysis and to underground infrastructure, from the laboratory to the in-situ scale.

I have been principal investigator and co-investigator on national and international projects on deep geological repositories, rock slope stability and landslide analysis, geohazard assessment and underground excavation design.

I teach Soil & Rock Mechanics, Landslides and Rock Slope Analysis, Underground Excavation, Dams and Hydroelectric Power Plants, and field excursions. I am a member of the International Society for Rock Mechanics (ISRM) and the American Rock Mechanics Association (ARMA), and a reviewer for Rock Mechanics and Rock Engineering, Landslides, and the Journal of Rock Mechanics and Geotechnical Engineering."""

CITATIONS_PER_YEAR = {
    "2013": 2, "2014": 5, "2015": 8, "2016": 14, "2017": 18, "2018": 26, "2019": 24,
    "2020": 54, "2021": 36, "2022": 49, "2023": 64, "2024": 69, "2025": 82, "2026": 118,
}

PUBLICATIONS = [
    ("Characterizing the influence of stress-induced microcracks on the laboratory strength and fracture development in brittle rocks using a finite-discrete element method-micro discrete fracture network FDEM-μDFN approach",
     "P Hamdi, D Stead, D Elmo", "Journal of Rock Mechanics and Geotechnical Engineering 7 (6), 609-625", 2015, 125, True),
    ("Damage characterization during laboratory strength testing: a 3D-finite-discrete element approach",
     "P Hamdi, D Stead, D Elmo", "Computers and Geotechnics 60, 33-46", 2014, 81, True),
    ("Use of an integrated finite/discrete element method-discrete fracture network approach to characterize surface subsidence associated with sub-level caving",
     "P Hamdi, D Stead, D Elmo, J Töyrä", "International Journal of Rock Mechanics and Mining Sciences 103, 55-67", 2018, 76, True),
    ("A multifunctional rock testing system for rock failure analysis under different stress states: Development and application",
     "S Li, J Hu, F Amann, L Li, H Liu, S Shi, P Hamdi", "Journal of Rock Mechanics and Geotechnical Engineering 14 (5), 1531-1544", 2022, 33, False),
    ("Investigating High-Strength Expanded Polystyrene (HS-EPS) as yielding support elements for tunnelling in squeezing ground conditions",
     "M Entfellner, P Hamdi, X Wang, H Wannenmacher, F Amann", "Tunnelling and Underground Space Technology 140, 105261", 2023, 27, False),
    ("Unloading induced absolute negative pore pressures in a low permeable clay shale",
     "K Khaledi, P Hamdi, L Winhausen, M Jalali, D Jaeggi, F Amann", "Engineering Geology 295, 106451", 2021, 25, False),
    ("A comparative study on methods for determining the hydraulic properties of a clay shale",
     "L Winhausen, A Amann-Hildenbrand, R Fink, M Jalali, K Khaledi, ...", "Geophysical Journal International 224 (3), 1523-1539", 2021, 23, False),
    ("Step path rock bridge percentage for analysis of slope stability",
     "WS Dershowitz, A Finnila, S Rogers, P Hamdi, KM Moffitt", "ARMA US Rock Mechanics/Geomechanics Symposium, ARMA-2017-1045", 2017, 23, False),
    ("Transversely isotropic slates subject to the compressive differential cyclic loading, Part I: experimental investigations",
     "ZY Song, T Zhang, WG Dang, P Hamdi, F Song, ZH Yu, Z Yang", "Rock Mechanics and Rock Engineering 57 (8), 5609-5635", 2024, 15, False),
    ("Back-analysis of the paraglacial slope failure at Grewingk Glacier and Lake, Alaska",
     "E Lemaire, A Dufresne, P Hamdi, B Higman, GJ Wolken, F Amann", "Landslides 21 (4), 775-789", 2024, 15, True),
]

EDUCATION = [
    dict(degree="PhD", field="Rock Mechanics / Geotechnics", institution="Simon Fraser University",
         location="Vancouver, Canada", start_year=2011, end_year=2015, order=1),
    dict(degree="MSc", field="Geotechnical Engineering", institution="Tafresh University, Department of Civil Engineering",
         location="Iran", start_year=2008, end_year=2010, order=2),
    dict(degree="BSc", field="Civil Engineering", institution="Urmia University, Department of Civil Engineering",
         location="Iran", start_year=2004, end_year=2008, order=3),
]

EXPERIENCE = [
    dict(role="Senior Scientist, Leader of the Rock Mechanics Group and Lecturer", organization="RWTH Aachen University",
         location="Aachen, Germany", start_year=2018, order=1),
    dict(role="Rock Mechanics Engineer", organization="Golder Associates Ltd.", location="Vancouver, Canada",
         start_year=2015, end_year=2018, order=2),
    dict(role="Research Assistant", organization="Simon Fraser University", location="Vancouver, Canada",
         start_year=2011, end_year=2015, order=3),
    dict(role="Research Assistant", organization="Tafresh University", location="Iran",
         start_year=2008, end_year=2010, order=4),
]

PROJECTS = [
    dict(title="Progressive Excavation Disturbance Zone Evolution during and Post Mine-by Tunnelling (PRECODE)",
         summary="A 100 m experimental tunnel branching off the Bedretto tunnel in Ticino, Switzerland, instrumented to "
                 "monitor strain, pore pressure and micro-seismicity. The project studies how the excavation damage zone "
                 "forms and evolves, long-term fracture propagation, permeability changes and the impact on fault zones. "
                 "Partners: York University, Dalhousie University, ETH Zurich and BGE Tech.",
         role="Principal Investigator (with Florian Amann)", funder="Bundesgesellschaft für Endlagerung (BGE)",
         start_year=2021, end_year=2024, status=Project.ONGOING, order=1,
         link=f"{LIH}/cms/LIH/Forschung/Ingenieurgeologie/Aktuelle-Projekte/~pxmun/Progressive-Entwicklung-der-Auflockerung/1/?lidx=1"),
    dict(title="Understanding Failure Mechanism of Non-Persistent Discontinuities Using 3D-Printed Synthetic Rock Mass",
         summary="Laboratory tests on 3D-printed synthetic rock mass samples with known joint configurations, used to "
                 "calibrate numerical models and develop a constitutive model for rock mass strength. In collaboration "
                 "with GeoPrint at the University of Alberta, Canada.",
         role="Principal Investigator (with Florian Amann)", funder="German Research Foundation (DFG)",
         start_year=2021, end_year=2024, status=Project.ONGOING, order=2,
         link=f"{LIH}/cms/LIH/Forschung/Ingenieurgeologie/Aktuelle-Projekte/~pekiz/Verstaendnis-von-Versagensmechanismen-vo/?lidx=1"),
    dict(title="Landslide Dam Properties and Stability (LADY)",
         summary="Why do some landslide dams remain stable for thousands of years while others fail within months? "
                 "LADY combines dam mapping, lake water-balance analysis and numerical stability simulations to test "
                 "a new hypothesis.",
         role="Principal Investigator (with Anja Dufresne and Florian Amann)", funder="German Research Foundation (DFG)",
         status=Project.ONGOING, order=3, link=f"{LIH}/go/id/dalko/lidx/1"),
    dict(title="Long-term monitoring of unstable rock slopes in a permafrost environment in Canton of Glarus, Switzerland",
         status=Project.ONGOING, order=4),
    dict(title="Einstein Telescope EMR Site & Technology (E-TEST)",
         summary="Feasibility study and geological inventory of the subsurface in the Euregio Meuse-Rhine to find a site "
                 "for the Einstein Telescope gravitational-wave observatory. Led by the University of Liège with 11 "
                 "universities and institutions from Belgium, the Netherlands and Germany.",
         role="Principal Investigator at RWTH (with Florian Amann)", funder="Interreg V-A Euregio Meuse-Rhine",
         start_year=2020, end_year=2023, status=Project.COMPLETED, order=5, link=f"{LIH}/go/id/gtwmg/lidx/1"),
    dict(title="Rock Slope Response to Glacier Retreat (Grewingk Glacier and Lake, Alaska)",
         role="Principal Investigator (with Anja Dufresne and Florian Amann)", funder="German Research Foundation (DFG)",
         start_year=2020, end_year=2023, status=Project.COMPLETED, order=6, link=f"{LIH}/go/id/qwpq/lidx/1"),
    dict(title="Multidisciplinary Slope Stability Analysis, Hazard Assessment and Effective Mitigation Measures for "
               "Areas with Cultural and Social Significance",
         role="Principal Investigator", funder="German Research Foundation (DFG)", status=Project.COMPLETED, order=7),
    dict(title="Material Approach for Opalinus Clay",
         summary="Development and validation of a hydro-mechanical constitutive model for Opalinus Clay, based on "
                 "laboratory triaxial tests and implemented in MOOSE.",
         funder="Swiss Federal Nuclear Safety Inspectorate (ENSI)", start_year=2018, end_year=2021,
         status=Project.COMPLETED, order=8, link=f"{LIH}/go/id/rdsc/lidx/1"),
]

STUDENTS = [
    dict(name="TODO Student One", level="phd", topic="TODO: research topic", start_year=2023, order=1),
    dict(name="TODO Student Two", level="phd", topic="TODO: research topic", start_year=2024, order=2),
    dict(name="TODO Student Three", level="msc", topic="TODO: research topic", start_year=2025, order=3),
    dict(name="TODO Former Student", level="msc", topic="TODO: thesis topic", start_year=2021, end_year=2023,
         status=Student.ALUMNI, order=4),
]


class Command(BaseCommand):
    help = "Load starting content (real Scholar data + TODO placeholders). Use --force to overwrite."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete existing entries first.")

    def handle(self, *args, force=False, **opts):
        if Profile.objects.exists() and not force:
            self.stdout.write("Content already exists; nothing changed. Use --force to reset it.")
            return
        for model in (Education, Experience, Project, Student, Publication):
            model.objects.all().delete()

        profile = Profile.load()
        profile.name = "Dr. Pooya Hamdi"
        profile.title = "Senior Scientist & Leader of the Rock Mechanics Group"
        profile.affiliation = "Chair of Engineering Geology and Hydrogeology, RWTH Aachen University"
        profile.tagline = "Rock mechanics · Slope stability & landslides · Numerical modelling"
        profile.bio = BIO
        profile.research_interests = ("Rock mechanics, Rock engineering design, Numerical modelling, Rock slope stability "
                                      "and landslides, Underground infrastructure, Deep geological repositories")
        profile.email = "hamdi@lih.rwth-aachen.de"
        profile.linkedin_url = "https://www.linkedin.com/in/pooyahamdi"
        profile.scholar_url = SCHOLAR_URL
        profile.orcid_url = "https://orcid.org/0000-0002-3786-7914"
        profile.institution_url = RWTH_URL
        profile.supervision_summary = "Over 15 MSc and BSc theses (co-)supervised since 2018."
        profile.save()

        stats = ScholarStats.load()
        stats.citations, stats.citations_recent = 575, 418
        stats.h_index, stats.h_index_recent = 12, 11
        stats.i10_index, stats.i10_index_recent = 14, 11
        stats.recent_since = 2021
        stats.citations_per_year = CITATIONS_PER_YEAR
        stats.last_updated = timezone.now()
        stats.save()

        for title, authors, venue, year, cites, _ in PUBLICATIONS:
            Publication.objects.create(title=title, authors=authors, venue=venue, year=year,
                                       citations=cites)
        for row in EDUCATION:
            Education.objects.create(**row)
        for row in EXPERIENCE:
            Experience.objects.create(**row)
        for row in PROJECTS:
            Project.objects.create(**row)
        for row in STUDENTS:
            Student.objects.create(**row)

        self.stdout.write(self.style.SUCCESS("Seeded. Replace the TODO entries in /admin."))
