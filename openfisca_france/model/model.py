# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import collections
from datetime import date

from openfisca_core.columns import AgeCol, BoolCol, EnumCol, FloatCol, IntCol
from openfisca_core.enumerations import Enum
from openfisca_core.formulas import AlternativeFormula, SimpleFormula

from .. import entities
from . import calage as cl
from . import common as cm
from .cotisations_sociales import capital as cs_capital
from .cotisations_sociales import travail as cs_travail
from .cotisations_sociales import remplacement as cs_remplac
from .cotisations_sociales import lps as cs_lps  # TODO: remove frome here
from . import inversion_revenus as inv_rev
from . import irpp as ir
from . import irpp_charges_deductibles as cd
from . import irpp_credits_impots as ci
from . import irpp_plus_values_immo as immo
from . import irpp_reductions_impots as ri
from . import isf as isf
from . import lgtm as lg
from . import mini as ms
from . import pfam as pf
from . import th as th


def build_alternative_formula_couple(name, functions, column):
    assert isinstance(name, basestring), name
    name = unicode(name)
    assert isinstance(functions, list), functions
    assert column.function is None

    alternative_formulas_constructor = []
    for function in functions:
        formula_class = type(name.encode('utf-8'), (SimpleFormula,), dict(
            function = staticmethod(function),
            ))
        formula_class.extract_parameters()
        alternative_formulas_constructor.append(formula_class)
    column.formula_constructor = formula_class = type(name.encode('utf-8'), (AlternativeFormula,), dict(
        alternative_formulas_constructor = alternative_formulas_constructor,
        ))
    if column.label is None:
        column.label = name
    assert column.name is None
    column.name = name

    entity_column_by_name = entities.entity_class_by_symbol[column.entity].column_by_name
    assert name not in entity_column_by_name, name
    entity_column_by_name[name] = column

    return (name, column)


def build_simple_formula_couple(name, column):
    assert isinstance(name, basestring), name
    name = unicode(name)

    column.formula_constructor = formula_class = type(name.encode('utf-8'), (SimpleFormula,), dict(
        function = staticmethod(column.function),
        ))
    formula_class.extract_parameters()
    del column.function
    if column.label is None:
        column.label = name
    assert column.name is None
    column.name = name

    entity_column_by_name = entities.entity_class_by_symbol[column.entity].column_by_name
    assert name not in entity_column_by_name, name
    entity_column_by_name[name] = column

    return (name, column)


prestation_by_name = collections.OrderedDict((
    ############################################################
    # Reproduction des pondérations
    ############################################################
    build_simple_formula_couple('mhsup', FloatCol(function = cs_travail._mhsup)),
    build_simple_formula_couple('alv', FloatCol(function = ir._alv)),

    ############################################################
    # Cotisations sociales
    ############################################################

    # Salaires
    build_simple_formula_couple('type_sal', EnumCol(function = cs_travail._type_sal, label = u"Catégorie de salarié",
        enum = Enum([
            u"prive_non_cadre",
            u"prive_cadre",
            u"public_titulaire_etat",
            u"public_titulaire_militaire",
            u"public_titulaire_territoriale",
            u"public_titulaire_hospitaliere",
            u"public_non_titulaire",
             ]),
         )),
    build_simple_formula_couple('salbrut', FloatCol(function = inv_rev._salbrut, label = u"Salaire brut ou traitement indiciaire brut")),
    build_simple_formula_couple('primes', FloatCol(function = cs_travail._primes, label = u"Primes et indemnités des fonctionnaires")),
    build_simple_formula_couple('sal_h_b', FloatCol(function = cs_travail._sal_h_b, label = u"Salaire horaire brut")),
    build_simple_formula_couple('taille_entreprise', EnumCol(function = cs_travail._taille_entreprise,
                                    label = u"Catégorie de taille d'entreprise (pour calcul des cotisations sociales)",
                                    enum = Enum([u"Non pertinent",
                                                 u"Moins de 10 salariés",
                                                 u"De 10 à 19 salariés",
                                                 u"De 20 à 249 salariés",
                                                 u"Plus de 250 salariés"]))),

    build_simple_formula_couple('cotpat_contrib', FloatCol(function = cs_travail._cotpat_contrib, label = u"Cotisations sociales patronales contributives")),
    build_simple_formula_couple('taux_accident_travail', FloatCol(function = cs_travail._taux_accident_travail, label = u"Cotisations sociales patronales : accident du travail et maladies professionnelles")),
    build_simple_formula_couple('cotpat_accident', FloatCol(function = cs_travail._cotpat_accident, label = u"Cotisations sociales patronales : accident du travail et maladies professionnelles")),
    build_simple_formula_couple('cotpat_noncontrib', FloatCol(function = cs_travail._cotpat_noncontrib, label = u"Cotisations sociales patronales non contributives")),
    build_simple_formula_couple('cotpat_main_d_oeuvre', FloatCol(function = cs_travail._cotpat_main_d_oeuvre, label = u"Cotisations sociales patronales main d'oeuvre")),
    build_simple_formula_couple('cotpat_transport', FloatCol(function = cs_travail._cotpat_transport, label = u"Cotisations sociales patronales: versement transport")),
    build_simple_formula_couple('cotpat', FloatCol(function = cs_travail._cotpat, label = u"Cotisations sociales patronales")),
    build_simple_formula_couple('alleg_fillon', FloatCol(function = cs_travail._alleg_fillon, label = u"Allègements Fillon sur les bas salaires")),
    build_simple_formula_couple('alleg_cice', FloatCol(function = cs_travail._alleg_cice, label = u"Crédit d'impôt compétitivité emploi")),
    build_simple_formula_couple('taxes_sal', FloatCol(function = cs_travail._taxes_sal, label = u"Taxes sur les salaires pour les employeurs non soumis à la TVA")),
    build_simple_formula_couple('tehr', FloatCol(function = cs_travail._tehr, label = u"taxe exceptionnelle de solidarité sur les très hautes rémunérations")),
    build_simple_formula_couple('salsuperbrut', FloatCol(function = cs_travail._salsuperbrut, label = u"Salaires super bruts")),

    build_simple_formula_couple('cotsal_contrib', FloatCol(function = cs_travail._cotsal_contrib, label = u"Cotisations sociales salariales contributives")),
    build_simple_formula_couple('cotsal_noncontrib', FloatCol(function = cs_travail._cotsal_noncontrib, label = u"Cotisations sociales non salariales non-contributives")),
    build_simple_formula_couple('cotsal', FloatCol(function = cs_travail._cotsal, label = u"Cotisations sociales salariales")),

    build_simple_formula_couple('csgsald', FloatCol(function = cs_travail._csgsald, label = u"CSG déductible sur les salaires")),
    build_simple_formula_couple('csgsali', FloatCol(function = cs_travail._csgsali, label = u"CSG imposables sur les salaires")),
    build_simple_formula_couple('crdssal', FloatCol(function = cs_travail._crdssal, label = u"CRDS sur les salaires")),
    build_simple_formula_couple('sal', FloatCol(function = cs_travail._sal, label = u"Salaires imposables")),
    build_simple_formula_couple('salnet', FloatCol(function = cs_travail._salnet, label = u"Salaires nets d'après définition INSEE")),

    # Fonctionnaires
    build_simple_formula_couple('indemnite_residence', FloatCol(function = cs_travail._indemnite_residence, label = u"Indemnité de résidence (fonction publique)")),
    build_simple_formula_couple('supp_familial_traitement', FloatCol(function = cs_travail._supp_familial_traitement,
        label = u"Supplément familial de traitement (fonction publique)", start = date(2011, 1, 1))),  # TODO: check this curious starting date
    build_simple_formula_couple('cot_pat_pension_civile', FloatCol(function = cs_travail._cot_pat_pension_civile, label = u"Cotisation patronale pension civile")),
    build_simple_formula_couple('cot_sal_pension_civile', FloatCol(function = cs_travail._cot_sal_pension_civile, label = u"Cotisation salariale pension civile")),
    build_simple_formula_couple('cot_pat_rafp', FloatCol(function = cs_travail._cot_pat_rafp, label = u"Cotisation patronale RAFP")),
    build_simple_formula_couple('cot_sal_rafp', FloatCol(function = cs_travail._cot_sal_rafp, label = u"Cotisation salariale RAFP")),

    # Revenus non-salariés
    build_simple_formula_couple('rev_microsocial', FloatCol(function = cs_travail._rev_microsocial,
        label = u"Revenu net des cotisations sociales pour le régime microsocial", start = date(2009, 1, 1))),

    # Allocations chômage
    build_simple_formula_couple('chobrut', FloatCol(function = inv_rev._chobrut, label = u"Allocations chômage brutes")),
    build_simple_formula_couple('csgchod', FloatCol(function = cs_remplac._csgchod, label = u"CSG déductible sur les allocations chômage")),
    build_simple_formula_couple('csgchoi', FloatCol(function = cs_remplac._csgchoi, label = u"CSG imposable sur les allocations chômage")),
    build_simple_formula_couple('crdscho', FloatCol(function = cs_remplac._crdscho, label = u"CRDS sur les allocations chômage")),
    build_simple_formula_couple('cho', FloatCol(function = cs_remplac._cho, label = u"Allocations chômage imposables")),
    build_simple_formula_couple('chonet', FloatCol(function = cs_remplac._chonet, label = u"Allocations chômage nettes")),

    # Pensions
    build_simple_formula_couple('rstbrut', FloatCol(function = cs_remplac._rstbrut, label = u"Pensions de retraite brutes")),
    build_simple_formula_couple('csgrstd', FloatCol(function = cs_remplac._csgrstd, label = u"CSG déductible sur les pensions de retraite")),
    build_simple_formula_couple('csgrsti', FloatCol(function = cs_remplac._csgrsti, label = u"CSG imposable sur les pensions de retraite")),
    build_simple_formula_couple('crdsrst', FloatCol(function = cs_remplac._crdsrst, label = u"CRDS sur les pensions de retraite")),
    build_simple_formula_couple('rst', FloatCol(function = cs_remplac._rst, label = u"Pensions de retraite imposables")),
    build_simple_formula_couple('rstnet', FloatCol(function = cs_remplac._rstnet, label = u"Pensions de retraite nettes")),
    build_simple_formula_couple('casa', FloatCol(function = cs_remplac._casa, label = u"Contribution additionnelle de solidarité et d'autonomie", start = date(2013, 4, 1))),

    # Revenus du capital soumis au prélèvement libératoire
    build_simple_formula_couple('csg_cap_lib', FloatCol(function = cs_capital._csg_cap_lib, label = u"CSG sur les revenus du capital soumis au prélèvement libératoire")),
    build_simple_formula_couple('crds_cap_lib', FloatCol(function = cs_capital._crds_cap_lib, label = u"CRDS sur les revenus du capital soumis au prélèvement libératoire")),
    build_simple_formula_couple('prelsoc_cap_lib', FloatCol(function = cs_capital._prelsoc_cap_lib, label = u"Prélèvements sociaux sur les revenus du capital soumis au prélèvement libératoire")),

    # Revenus du capital soumis au barème
    build_simple_formula_couple('csg_cap_bar', FloatCol(function = cs_capital._csg_cap_bar, label = u"CSG sur les revenus du capital soumis au barème")),
    build_simple_formula_couple('crds_cap_bar', FloatCol(function = cs_capital._crds_cap_bar, label = u"CRDS sur les revenus du capital soumis au barème")),
    build_simple_formula_couple('prelsoc_cap_bar', FloatCol(function = cs_capital._prelsoc_cap_bar, label = u"Prélèvements sociaux sur les revenus du capital soumis au barème")),

    # Revenus fonciers (sur les foyers)
    build_simple_formula_couple('csg_fon', FloatCol(function = cs_capital._csg_fon, entity = "foy", label = u"CSG sur les revenus fonciers")),
    build_simple_formula_couple('crds_fon', FloatCol(function = cs_capital._crds_fon, entity = "foy", label = u"CRDS sur les revenus fonciers")),
    build_simple_formula_couple('prelsoc_fon', FloatCol(function = cs_capital._prelsoc_fon, entity = "foy", label = u"Prélèvements sociaux sur les revenus fonciers")),

    # Plus values de cessions de valeurs mobilières
    build_simple_formula_couple('csg_pv_mo', FloatCol(function = cs_capital._csg_pv_mo, entity = "foy", label = u"CSG sur les plus-values de cession de valeurs mobilières")),
    build_simple_formula_couple('crds_pv_mo', FloatCol(function = cs_capital._crds_pv_mo, entity = "foy", label = u"CRDS sur les plus-values de cession de valeurs mobilières")),
    build_simple_formula_couple('prelsoc_pv_mo', FloatCol(function = cs_capital._prelsoc_pv_mo, entity = "foy", label = u"Prélèvements sociaux sur les plus-values de cession de valeurs mobilières")),

    # Plus-values immobilières
    build_simple_formula_couple('csg_pv_immo', FloatCol(function = cs_capital._csg_pv_immo, entity = "foy", label = u"CSG sur les plus-values immobilières")),
    build_simple_formula_couple('crds_pv_immo', FloatCol(function = cs_capital._crds_pv_immo, entity = "foy", label = u"CRDS sur les plus-values immobilières")),
    build_simple_formula_couple('prelsoc_pv_immo', FloatCol(function = cs_capital._prelsoc_pv_immo, entity = "foy", label = u"Prélèvements sociaux sur les plus-values immobilières")),

    # Réforme Landais-Pikettty-Saez TODO: move out form here
    build_simple_formula_couple('base_csg', FloatCol(function = cs_lps._base_csg)),
    build_simple_formula_couple('ir_lps', FloatCol(function = cs_lps._ir_lps, start = date(2010, 1, 1))),

    ############################################################
    # Impôt sur le revenu
    ############################################################

    build_alternative_formula_couple(
        'age',
        [
            ir._age_from_birth,
            ir._age_from_agem,
            ],
        AgeCol(label = u"Âge (en années)", val_type = "age"),
        ),
    build_alternative_formula_couple(
        'agem',
        [
            ir._agem_from_birth,
            ir._agem_from_age,
            ],
        AgeCol(label = u"Âge (en mois)", val_type = "months"),
        ),

    build_simple_formula_couple('nbF', IntCol(function = ir._nbF, cerfa_field = u'F', entity = 'foy',
        label = u"Nombre d'enfants à charge  non mariés de moins de 18 ans au 1er janvier de l'année de perception des"
            u" revenus, ou nés en durant la même année ou handicapés quel que soit leur âge")),
    build_simple_formula_couple('nbG', IntCol(function = ir._nbG, cerfa_field = u'G', entity = 'foy',
        label = u"Nombre d'enfants à charge titulaires de la carte d'invalidité")),
    # TODO: vérifier si c'est bien ça pour la nbH et la caseH qui suit
    build_simple_formula_couple('nbH', IntCol(function = ir._nbH, cerfa_field = u'H', entity = 'foy',
        label = u"Nombre d'enfants à charge en résidence alternée, non mariés de moins de 18 ans au 1er janvier de"
            u" l'année de perception des revenus, ou nés durant la même année ou handicapés quel que soit leur âge")),
    build_simple_formula_couple('nbI', IntCol(function = ir._nbI, cerfa_field = u'I', entity = 'foy',
        label = u"Nombre d'enfants à charge en résidence alternée titulaires de la carte d'invalidité")),
    build_simple_formula_couple('nbJ', IntCol(function = ir._nbJ, cerfa_field = u'J', entity = 'foy',
        label = u"Nombre d'enfants majeurs célibataires sans enfant")),
#    build_simple_formula_couple('nbN', IntCol(function = ir._nbN, cerfa_field = u'N', entity = 'foy',
#        label = u"Nombre d'enfants mariés/pacsés et d'enfants non mariés chargés de famille")),
#    build_simple_formula_couple('nbR', IntCol(function = ir._nbR, cerfa_field = u'R', entity = 'foy',
#        label = u"Nombre de titulaires de la carte invalidité d'au moins 80 %")),

    build_simple_formula_couple('marpac', BoolCol(function = ir._marpac, entity = 'foy')),
    build_simple_formula_couple('celdiv', BoolCol(function = ir._celdiv, entity = 'foy')),
    build_simple_formula_couple('veuf', BoolCol(function = ir._veuf, entity = 'foy')),
    build_simple_formula_couple('jveuf', BoolCol(function = ir._jveuf, entity = 'foy')),
    build_simple_formula_couple('nbptr', FloatCol(function = ir._nbptr, entity = 'foy', label = u"Nombre de parts")),
    build_simple_formula_couple('rbg', FloatCol(function = ir._rbg, entity = 'foy', label = u"Revenu brut global")),

    # charges déductibles
    build_simple_formula_couple('cd_penali', FloatCol(function = cd._cd_penali, entity = 'foy')),
    build_simple_formula_couple('cd_acc75a', FloatCol(function = cd._cd_acc75a, entity = 'foy')),
    build_simple_formula_couple('cd_percap', FloatCol(function = cd._cd_percap, entity = 'foy', start = date(2002, 1, 1), end = date(2006, 12, 31))),
    build_simple_formula_couple('cd_deddiv', FloatCol(function = cd._cd_deddiv, entity = 'foy')),
    build_simple_formula_couple('cd_doment', FloatCol(function = cd._cd_doment, entity = 'foy', start = date(2002, 1, 1), end = date(2005, 12, 31))),
    build_simple_formula_couple('cd_eparet', FloatCol(function = cd._cd_eparet, entity = 'foy', start = date(2004, 1, 1))),
    build_simple_formula_couple('cd_sofipe', FloatCol(function = cd._cd_sofipe, entity = 'foy', start = date(2002, 1, 1), end = date(2006, 12, 31))),
    build_simple_formula_couple('cd_cinema', FloatCol(function = cd._cd_cinema, entity = 'foy', start = date(2002, 1, 1), end = date(2005, 12, 31))),
    build_simple_formula_couple('cd_ecodev', FloatCol(function = cd._cd_ecodev, entity = 'foy', start = date(2007, 1, 1), end = date(2008, 12, 31))),
    build_simple_formula_couple('cd_grorep', FloatCol(function = cd._cd_grorep, entity = 'foy', start = date(2009, 1, 1))),

    build_simple_formula_couple('charges_deduc_reforme', FloatCol(function = cd._charges_deduc_reforme, entity = 'foy')),
    build_simple_formula_couple('charge_loyer', FloatCol(function = cd._charge_loyer, entity = 'foy')),

    build_simple_formula_couple('rbg_int', FloatCol(function = cd._rbg_int, entity = 'foy', label = u"Revenu brut global intermédiaire")),
    build_simple_formula_couple('cd1', FloatCol(function = cd._cd1, entity = 'foy', label = u"Charges déductibles non plafonnées")),
    build_simple_formula_couple('cd2', FloatCol(function = cd._cd2, entity = 'foy', label = u"Charges déductibles plafonnées", start = date(2002, 1, 1), end = date(2008, 12, 31))),
    build_simple_formula_couple('charges_deduc', FloatCol(function = cd._charges_deduc, entity = 'foy', label = u"Charges déductibles")),

    build_simple_formula_couple('rfr_cd', FloatCol(function = cd._rfr_cd, entity = 'foy', label = u"Charges déductibles entrant dans le revenus fiscal de référence")),  # TODO:

    build_simple_formula_couple('rng', FloatCol(function = ir._rng, entity = 'foy', label = u"Revenu net global")),
    build_simple_formula_couple('rni', FloatCol(function = ir._rni, entity = 'foy', label = u"Revenu net imposable")),

    build_simple_formula_couple('abat_spe', FloatCol(function = ir._abat_spe, entity = 'foy', label = u"Abattements spéciaux")),
    build_simple_formula_couple('alloc', FloatCol(function = ir._alloc, entity = 'foy', label = u"Allocation familiale pour l'ir")),
    build_simple_formula_couple('deficit_ante', FloatCol(function = ir._deficit_ante, entity = 'foy', label = u"Déficit global antérieur")),

    build_simple_formula_couple('rev_sal', FloatCol(function = ir._rev_sal)),
    build_simple_formula_couple('salcho_imp', FloatCol(function = ir._salcho_imp)),
    build_simple_formula_couple('rev_pen', FloatCol(function = ir._rev_pen)),
    build_simple_formula_couple('pen_net', FloatCol(function = ir._pen_net)),
    build_simple_formula_couple('indu_plaf_abat_pen', FloatCol(function = ir._indu_plaf_abat_pen, entity = 'foy')),
    build_simple_formula_couple('abat_sal_pen', FloatCol(function = ir._abat_sal_pen, start = date(2002, 1, 1), end = date(2005, 12, 31))),
    build_simple_formula_couple('sal_pen_net', FloatCol(function = ir._sal_pen_net)),
    build_simple_formula_couple('rto', FloatCol(function = ir._rto, label = u'Rentes viagères (rentes à titre onéreux)')),
    build_simple_formula_couple('rto_net', FloatCol(function = ir._rto_net, label = u'Rentes viagères après abattements')),
    build_simple_formula_couple('tspr', FloatCol(function = ir._tspr)),

    build_simple_formula_couple('rev_cat_tspr', FloatCol(function = ir._rev_cat_tspr, entity = 'foy', label = u"Revenu catégoriel - Salaires, pensions et rentes")),
    build_simple_formula_couple('rev_cat_rvcm', FloatCol(function = ir._rev_cat_rvcm, entity = 'foy', label = u'Revenu catégoriel - Capitaux')),
    build_simple_formula_couple('rev_cat_rpns', FloatCol(function = ir._rev_cat_rpns, entity = 'foy', label = u'Revenu catégoriel - Rpns')),
    build_simple_formula_couple('rev_cat_rfon', FloatCol(function = ir._rev_cat_rfon, entity = 'foy', label = u'Revenu catégoriel - Foncier')),
    build_simple_formula_couple('rev_cat_pv', FloatCol(function = ir._rev_cat_pv, entity = 'foy', label = u'Revenu catégoriel - Plus-values', start = date(2013, 1, 1))),
    build_simple_formula_couple('rev_cat', FloatCol(function = ir._rev_cat, entity = 'foy', label = u"Revenus catégoriels")),

    build_simple_formula_couple('deficit_rcm', FloatCol(function = ir._deficit_rcm, entity = 'foy', label = u'Deficit capitaux mobiliers')),
    build_simple_formula_couple('csg_deduc_patrimoine_simulated', FloatCol(function = ir._csg_deduc_patrimoine_simulated, entity = 'foy',
        label = u'Csg déductible sur le patrimoine simulée')),
    build_simple_formula_couple('csg_deduc_patrimoine', FloatCol(function = ir._csg_deduc_patrimoine, entity = 'foy', label = u'Csg déductible sur le patrimoine')),
    build_simple_formula_couple('csg_deduc', FloatCol(function = ir._csg_deduc, entity = 'foy', label = u'Csg déductible sur le patrimoine')),

    build_simple_formula_couple('plus_values', FloatCol(function = ir._plus_values, entity = 'foy')),
    build_simple_formula_couple('ir_brut', FloatCol(function = ir._ir_brut, entity = 'foy')),
    build_simple_formula_couple('nb_pac', FloatCol(function = ir._nb_pac, entity = 'foy')),
    build_simple_formula_couple('nb_adult', FloatCol(function = ir._nb_adult, entity = 'foy')),
    build_simple_formula_couple('ir_ss_qf', FloatCol(function = ir._ir_ss_qf, entity = 'foy')),
    build_simple_formula_couple('ir_plaf_qf', FloatCol(function = ir._ir_plaf_qf, entity = 'foy')),
    build_simple_formula_couple('avantage_qf', FloatCol(function = ir._avantage_qf, entity = 'foy')),
    build_simple_formula_couple('nat_imp', FloatCol(function = ir._nat_imp, entity = 'foy')),
    build_simple_formula_couple('decote', FloatCol(function = ir._decote, entity = 'foy')),

    # réductions d'impots
    build_simple_formula_couple('donapd', FloatCol(function = ri._donapd, entity = 'foy')),
    build_simple_formula_couple('dfppce', FloatCol(function = ri._dfppce, entity = 'foy')),
    build_simple_formula_couple('cotsyn', FloatCol(function = ri._cotsyn, entity = 'foy')),
    build_simple_formula_couple('resimm', FloatCol(function = ri._resimm, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('patnat', FloatCol(function = ri._patnat, entity = 'foy', start = date(2010, 1, 1))),
    build_simple_formula_couple('sofipe', FloatCol(function = ri._sofipe, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('saldom', FloatCol(function = ri._saldom, entity = 'foy', start = date(2007, 1, 1))),
    build_simple_formula_couple('intagr', FloatCol(function = ri._intagr, entity = 'foy', start = date(2005, 1, 1))),
    build_simple_formula_couple('prcomp', FloatCol(function = ri._prcomp, entity = 'foy')),
    build_simple_formula_couple('spfcpi', FloatCol(function = ri._spfcpi, entity = 'foy')),
    build_simple_formula_couple('mohist', FloatCol(function = ri._mohist, entity = 'foy', start = date(2008, 1, 1))),
    build_simple_formula_couple('sofica', FloatCol(function = ri._sofica, entity = 'foy', start = date(2006, 1, 1))),
    build_simple_formula_couple('cappme', FloatCol(function = ri._cappme, entity = 'foy')),
    build_simple_formula_couple('repsoc', FloatCol(function = ri._repsoc, entity = 'foy', start = date(2003, 1, 1))),
    build_simple_formula_couple('invfor', FloatCol(function = ri._invfor, entity = 'foy')),
    build_simple_formula_couple('deffor', FloatCol(function = ri._deffor, entity = 'foy', start = date(2006, 1, 1))),
    build_simple_formula_couple('daepad', FloatCol(function = ri._daepad, entity = 'foy')),
    build_simple_formula_couple('rsceha', FloatCol(function = ri._rsceha, entity = 'foy')),
    build_simple_formula_couple('invlst', FloatCol(function = ri._invlst, entity = 'foy', start = date(2004, 1, 1))),
    build_simple_formula_couple('domlog', FloatCol(function = ri._domlog, entity = 'foy', start = date(2002, 1, 1), end = date(2009, 12, 31))),
    build_simple_formula_couple('adhcga', FloatCol(function = ri._adhcga, entity = 'foy')),
    build_simple_formula_couple('creaen', FloatCol(function = ri._creaen, entity = 'foy', start = date(2006, 1, 1))),
    build_simple_formula_couple('ecpess', FloatCol(function = ri._ecpess, entity = 'foy')),
    build_simple_formula_couple('scelli', FloatCol(function = ri._scelli, entity = 'foy', start = date(2009, 1, 1), end = date(2010, 12, 31))),
    build_simple_formula_couple('locmeu', FloatCol(function = ri._locmeu, entity = 'foy', start = date(2009, 1, 1), end = date(2010, 12, 31))),
    build_simple_formula_couple('doment', FloatCol(function = ri._doment, entity = 'foy')),
    build_simple_formula_couple('domsoc', FloatCol(function = ri._domsoc, entity = 'foy')),
    build_simple_formula_couple('intemp', FloatCol(function = ri._intemp, entity = 'foy', start = date(2002, 1, 1), end = date(2003, 12, 31))),
    build_simple_formula_couple('garext', FloatCol(function = ri._garext, entity = 'foy', start = date(2002, 1, 1), end = date(2005, 12, 31))),
    build_simple_formula_couple('assvie', FloatCol(function = ri._assvie, entity = 'foy', start = date(2002, 1, 1), end = date(2004, 12, 31))),
    build_simple_formula_couple('invrev', FloatCol(function = ri._invrev, entity = 'foy', start = date(2002, 1, 1), end = date(2003, 12, 31))),
    build_simple_formula_couple('intcon', FloatCol(function = ri._intcon, entity = 'foy', start = date(2004, 1, 1), end = date(2005, 12, 31))),
    build_simple_formula_couple('ecodev', FloatCol(function = ri._ecodev, entity = 'foy', start = date(2009, 1, 1), end = date(2009, 12, 31))),

    build_simple_formula_couple('nb_pac2', FloatCol(function = ci._nb_pac2, entity = 'foy')),

    build_simple_formula_couple('ip_net', FloatCol(function = ir._ip_net, entity = 'foy')),
    build_simple_formula_couple('reductions', FloatCol(function = ri._reductions, entity = 'foy')),
    build_simple_formula_couple('iaidrdi', FloatCol(function = ir._iaidrdi, entity = 'foy')),
    build_simple_formula_couple('teicaa', FloatCol(function = ir._teicaa, entity = 'foy')),
    build_simple_formula_couple('cont_rev_loc', FloatCol(function = ir._cont_rev_loc, entity = 'foy', start = date(2001, 1, 1))),
    build_simple_formula_couple('iai', FloatCol(function = ir._iai, entity = 'foy')),
    build_simple_formula_couple('cehr', FloatCol(function = ir._cehr, entity = 'foy', label = u"Contribution exceptionnelle sur les hauts revenus")),
 #   build_simple_formula_couple('cesthra', FloatCol(function = ir._cesthra, entity = 'foy', start = date(2013, 1, 1))), PLF 2013, amendement rejeté
    build_simple_formula_couple('imp_lib', FloatCol(function = ir._imp_lib, entity = 'foy', end = date(2012, 12, 31)),),  # TODO: Check - de 2000euros
    build_simple_formula_couple('assiette_vente', FloatCol(function = ir._micro_social_vente, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('assiette_service', FloatCol(function = ir._micro_social_service, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('assiette_proflib', FloatCol(function = ir._micro_social_proflib, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('microsocial', FloatCol(function = ir._micro_social, entity = 'foy')),

    # Prime pour l'emploi
    build_simple_formula_couple('ppe_coef', FloatCol(function = ir._ppe_coef, entity = 'foy')),
    build_simple_formula_couple('ppe_base', FloatCol(function = ir._ppe_base)),
    build_simple_formula_couple('ppe_coef_tp', FloatCol(function = ir._ppe_coef_tp)),
    build_simple_formula_couple('ppe_elig', BoolCol(function = ir._ppe_elig, entity = 'foy')),
    build_simple_formula_couple('ppe_elig_i', BoolCol(function = ir._ppe_elig_i)),
    build_simple_formula_couple('ppe_rev', FloatCol(function = ir._ppe_rev)),
    build_simple_formula_couple('ppe_brute', FloatCol(function = ir._ppe_brute, entity = 'foy', label = u"Prime pour l'emploi brute")),
    build_simple_formula_couple('ppe', FloatCol(function = ir._ppe, entity = 'foy', label = u"Prime pour l'emploi")),

    # Autres crédits d'impôts
    build_simple_formula_couple('creimp', FloatCol(function = ci._creimp, entity = 'foy')),
    build_simple_formula_couple('accult', FloatCol(function = ci._accult, entity = 'foy')),
    build_simple_formula_couple('percvm', FloatCol(function = ci._percvm, entity = 'foy', start = date(2010, 1, 1))),
    build_simple_formula_couple('direpa', FloatCol(function = ci._direpa, entity = 'foy')),
    build_simple_formula_couple('mecena', FloatCol(function = ci._mecena, entity = 'foy', start = date(2003, 1, 1))),
    build_simple_formula_couple('prlire', FloatCol(function = ci._prlire, entity = 'foy', label = u"Prélèvement libératoire à restituer (case 2DH)", end = date(2012, 12, 31))),
    build_simple_formula_couple('aidper', FloatCol(function = ci._aidper, entity = 'foy')),
    build_simple_formula_couple('quaenv', FloatCol(function = ci._quaenv, entity = 'foy', start = date(2005, 1, 1))),
    build_simple_formula_couple('drbail', FloatCol(function = ci._drbail, entity = 'foy')),
    build_simple_formula_couple('ci_garext', FloatCol(function = ci._ci_garext, entity = 'foy', start = date(2005, 1, 1))),
    build_simple_formula_couple('preetu', FloatCol(function = ci._preetu, entity = 'foy', start = date(2005, 1, 1))),
    build_simple_formula_couple('saldom2', FloatCol(function = ci._saldom2, entity = 'foy', start = date(2007, 1, 1))),
    build_simple_formula_couple('inthab', FloatCol(function = ci._inthab, entity = 'foy', start = date(2007, 1, 1))),
    build_simple_formula_couple('assloy', FloatCol(function = ci._assloy, entity = 'foy', start = date(2005, 1, 1))),
    build_simple_formula_couple('autent', FloatCol(function = ci._autent, entity = 'foy', start = date(2009, 1, 1))),
    build_simple_formula_couple('acqgpl', FloatCol(function = ci._acqgpl, entity = 'foy', start = date(2002, 1, 1), end = date(2007, 12, 31))),
    build_simple_formula_couple('divide', FloatCol(function = ci._divide, entity = 'foy', start = date(2005, 1, 1), end = date(2009, 12, 31))),
    build_simple_formula_couple('aidmob', FloatCol(function = ci._aidmob, entity = 'foy', start = date(2005, 1, 1), end = date(2008, 12, 31))),

    build_simple_formula_couple('jeunes', FloatCol(function = ci._jeunes, entity = 'foy', start = date(2005, 1, 1), end = date(2008, 12, 31))),

    build_simple_formula_couple('credits_impot', FloatCol(function = ci._credits_impot, entity = 'foy')),

    build_simple_formula_couple('irpp', FloatCol(function = ir._irpp, entity = 'foy', label = u"Impôt sur le revenu des personnes physiques")),

    build_simple_formula_couple('rfr', FloatCol(function = ir._rfr, entity = 'foy')),
    build_simple_formula_couple('rfr_rvcm', FloatCol(function = ir._rfr_rvcm, entity = 'foy')),

#    build_simple_formula_couple('alv', FloatCol(function = ir._alv)),
    build_simple_formula_couple('glo', FloatCol(function = ir._glo, label =u"Gain de levée d'options")),
    build_simple_formula_couple('rag', FloatCol(function = ir._rag)),
    build_simple_formula_couple('ric', FloatCol(function = ir._ric)),
    build_simple_formula_couple('rac', FloatCol(function = ir._rac)),
    build_simple_formula_couple('rnc', FloatCol(function = ir._rnc)),
    build_simple_formula_couple('rpns', FloatCol(function = ir._rpns)),
    build_simple_formula_couple('fon', FloatCol(function = ir._fon, entity = 'foy')),

    build_simple_formula_couple('rpns_mvct', FloatCol(function = ir._rpns_mvct)),
    build_simple_formula_couple('rpns_pvct', FloatCol(function = ir._rpns_pvct)),
    build_simple_formula_couple('rpns_mvlt', FloatCol(function = ir._rpns_mvlt)),
    build_simple_formula_couple('rpns_pvce', FloatCol(function = ir._rpns_pvce)),
    build_simple_formula_couple('rpns_exon', FloatCol(function = ir._rpns_exon)),
    build_simple_formula_couple('rpns_i', FloatCol(function = ir._rpns_i)),

    build_simple_formula_couple('rev_cap_bar', FloatCol(function = ir._rev_cap_bar, entity = 'foy')),
    build_simple_formula_couple('rev_cap_lib', FloatCol(function = ir._rev_cap_lib, entity = 'foy')),
    build_simple_formula_couple('avf', FloatCol(function = ir._avf, entity = 'foy')),

    ###########################################################
    # Impôt sur le revenu afférent à la plus-value immobilière
    ###########################################################

    build_simple_formula_couple('ir_pv_immo', FloatCol(function = immo._ir_pv_immo,
                              entity = 'foy',
                              label = u"Impôt sur le revenu afférent à la plus-value immobilière")),

    ############################################################
    # Impôt de solidarité sur la fortune
    ############################################################
    build_simple_formula_couple('isf_imm_bati', FloatCol(function = isf._isf_imm_bati, entity = 'foy')),
    build_simple_formula_couple('isf_imm_non_bati', FloatCol(function = isf._isf_imm_non_bati, entity = 'foy')),
    build_simple_formula_couple('isf_actions_sal', FloatCol(function = isf._isf_actions_sal, entity = 'foy', start = date(2006, 1, 1))),
    build_simple_formula_couple('isf_droits_sociaux', FloatCol(function = isf._isf_droits_sociaux, entity = 'foy')),
    build_simple_formula_couple('ass_isf', FloatCol(function = isf._ass_isf, entity = 'foy')),

    build_simple_formula_couple('isf_iai', FloatCol(function = isf._isf_iai, entity = 'foy')),
    build_simple_formula_couple('tot_impot', FloatCol(function = isf._tot_impot, entity = 'foy')),
    build_simple_formula_couple('isf_avant_plaf', FloatCol(function = isf._isf_avant_plaf, entity = 'foy')),
    build_simple_formula_couple('isf_avant_reduction', FloatCol(function = isf._isf_avant_reduction, entity = 'foy')),
    build_simple_formula_couple('isf_reduc_pac', FloatCol(function = isf._isf_reduc_pac, entity = 'foy')),
    build_simple_formula_couple('isf_inv_pme', FloatCol(function = isf._isf_inv_pme, entity = 'foy', start = date(2008, 1, 1))),
    build_simple_formula_couple('isf_org_int_gen', FloatCol(function = isf._isf_org_int_gen, entity = 'foy')),
    build_simple_formula_couple('revetproduits', FloatCol(function = isf._revetproduits, entity = 'foy')),
    build_simple_formula_couple('isf_apres_plaf', FloatCol(function = isf._isf_apres_plaf, entity = 'foy')),
    build_simple_formula_couple('decote_isf', FloatCol(function = isf._decote_isf, entity = 'foy', start = date(2013, 1, 1))),
    build_simple_formula_couple('isf_tot', FloatCol(function = isf._isf_tot, entity = 'foy')),

    ############################################################
    #                            Bouclier Fiscal
    ############################################################
    build_simple_formula_couple('rvcm_plus_abat', FloatCol(function = isf._rvcm_plus_abat, entity = 'foy')),
    build_simple_formula_couple('maj_cga', FloatCol(function = isf._maj_cga, entity = 'foy')),

    build_simple_formula_couple('bouclier_rev', FloatCol(function = isf._bouclier_rev,
                                entity = 'foy',
                                start = date(2006, 1, 1),
                                end = date(2010, 12, 31))),
    build_simple_formula_couple('bouclier_imp_gen', FloatCol(function = isf._bouclier_imp_gen,
                                    entity = 'foy',
                                    start = date(2006, 1, 1),
                                    end = date(2010, 12, 31))),
    build_simple_formula_couple('restitutions', FloatCol(function = isf._restitutions,
                                entity = 'foy',
                                start = date(2006, 1, 1),
                                end = date(2010, 12, 31))),
    build_simple_formula_couple('bouclier_sumimp', FloatCol(function = isf._bouclier_sumimp,
                                   entity = 'foy',
                                   start = date(2006, 1, 1),
                                   end = date(2010, 12, 31))),
    build_simple_formula_couple('bouclier_fiscal', FloatCol(function = isf._bouclier_fiscal,
                                   entity = 'foy',
                                   start = date(2006, 1, 1),
                                   end = date(2010, 12, 31))),

    # TODO: inclure aussi les dates si nécessaire start = date(2007,1,1)

    ############################################################
    # Prestations familiales
    ############################################################

    build_simple_formula_couple('etu', BoolCol(function = pf._etu, label = u"Indicatrice individuelle étudiant")),
    build_simple_formula_couple('biact', BoolCol(function = pf._biact, entity = 'fam', label = u"Indicatrice de biactivité")),
    build_simple_formula_couple('concub', BoolCol(function = pf._concub, entity = 'fam', label = u"Indicatrice de vie en couple")),
    build_simple_formula_couple('maries', BoolCol(function = pf._maries, entity = 'fam')),
    build_simple_formula_couple('nb_par', FloatCol(function = pf._nb_par, entity = 'fam', label = u"Nombre de parents")),
    build_simple_formula_couple('smic55', BoolCol(function = pf._smic55, label = u"Indicatrice individuelle d'un salaire supérieur à 55% du smic")),
    build_simple_formula_couple('isol', BoolCol(function = pf._isol, entity = 'fam')),

    build_simple_formula_couple('div', FloatCol(function = pf._div)),
    build_simple_formula_couple('rev_coll', FloatCol(function = pf._rev_coll)),
    build_simple_formula_couple('br_pf_i', FloatCol(function = pf._br_pf_i, label = 'Base ressource individuele des prestations familiales')),
    build_simple_formula_couple('br_pf', FloatCol(function = pf._br_pf, entity = 'fam', label = 'Base ressource des prestations familiales')),

    build_simple_formula_couple('af_nbenf', FloatCol(function = pf._af_nbenf, entity = 'fam', label = u"Nombre d'enfant au sens des AF")),
    build_simple_formula_couple('af_base', FloatCol(function = pf._af_base, entity = 'fam', label = 'Allocations familiales - Base')),
    build_simple_formula_couple('af_majo', FloatCol(function = pf._af_majo, entity = 'fam', label = 'Allocations familiales - Majoration pour age')),
    build_simple_formula_couple('af_forf', FloatCol(function = pf._af_forf, entity = 'fam', label = 'Allocations familiales - Forfait 20 ans', start = date(2003, 7, 1))),
    build_simple_formula_couple('af', FloatCol(function = pf._af, entity = 'fam', label = u"Allocations familiales")),

    build_simple_formula_couple('cf_temp', FloatCol(function = pf._cf, entity = 'fam', label = u"Complément familial avant d'éventuels cumuls")),
    build_simple_formula_couple('asf_elig', BoolCol(function = pf._asf_elig, entity = 'fam')),
    build_simple_formula_couple('asf', FloatCol(function = pf._asf, entity = 'fam', label = u"Allocation de soutien familial")),

    build_simple_formula_couple('ars', FloatCol(function = pf._ars, entity = 'fam', label = u"Allocation de rentrée scolaire")),


    build_simple_formula_couple('paje_base_temp', FloatCol(function = pf._paje_base, entity = 'fam', label = u"Allocation de base de la PAJE sans tenir compte d'éventuels cumuls", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_base', FloatCol(function = pf._paje_cumul, entity = 'fam', label = u"Allocation de base de la PAJE", start = date(2004, 1, 1))),

    build_simple_formula_couple('paje_nais', FloatCol(function = pf._paje_nais, entity = 'fam', label = u"Allocation de naissance de la PAJE", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_clca', FloatCol(function = pf._paje_clca, entity = 'fam', label = u"PAJE - Complément de libre choix d'activité", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_clca_taux_plein', BoolCol(function = pf._paje_clca_taux_plein, entity = 'fam', label = u"Indicatrice Clca taux plein", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_clca_taux_partiel', BoolCol(function = pf._paje_clca_taux_partiel, entity = 'fam', label = u"Indicatrice Clca taux partiel", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_colca', FloatCol(function = pf._paje_colca, entity = 'fam', label = u"PAJE - Complément optionnel de libre choix d'activité", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje_clmg', FloatCol(function = pf._paje_clmg, entity = 'fam', label = u"PAJE - Complément de libre choix du mode de garde", start = date(2004, 1, 1))),
    build_simple_formula_couple('paje', FloatCol(function = pf._paje, entity = 'fam', label = u"PAJE - Ensemble des prestations", start = date(2004, 1, 1))),


    build_simple_formula_couple('cf', FloatCol(function = pf._cf_cumul, entity = 'fam', label = u"Complément familial")),
    build_simple_formula_couple('aeeh', FloatCol(function = pf._aeeh, entity = 'fam', label = u"Allocation d'éducation de l'enfant handicapé")),

    build_simple_formula_couple('ape_temp', FloatCol(function = pf._ape, entity = 'fam', label = u"Allocation parentale d'éducation", end = date(2004, 1, 1))),
    build_simple_formula_couple('apje_temp', FloatCol(function = pf._apje, entity = 'fam', label = u"Allocation pour le jeune enfant", end = date(2004, 1, 1))),
    build_simple_formula_couple('ape', FloatCol(function = pf._ape_cumul, entity = 'fam', label = u"Allocation parentale d'éducation", end = date(2004, 1, 1))),
    build_simple_formula_couple('apje', FloatCol(function = pf._apje_cumul, entity = 'fam', label = u"Allocation pour le jeune enfant", end = date(2004, 1, 1))),

    build_simple_formula_couple('crds_pfam', FloatCol(function = pf._crds_pfam, entity = 'fam', label = u"CRDS (prestations familiales)")),

    # En fait en vigueur pour les enfants nés avant 2004 ...
    # TODO Gestion du cumul apje ape
    ############################################################
    # Allocations logement
    ############################################################

    build_simple_formula_couple('br_al', FloatCol(function = lg._br_al, entity = 'fam', label = u"Base ressource des allocations logement")),
    build_simple_formula_couple('al_pac', FloatCol(function = lg._al_pac, entity = 'fam', label = u"Nombre de personnes à charge au sens des allocations logement")),
    build_simple_formula_couple('al', FloatCol(function = lg._al, entity = 'fam', label = u"Allocation logement (indifferrenciée)")),
    build_simple_formula_couple('alf', FloatCol(function = lg._alf, entity = 'fam', label = u"Allocation logement familiale")),
    build_simple_formula_couple('als', FloatCol(function = lg._als, entity = 'fam', label = u"Allocation logement sociale")),
    build_simple_formula_couple('als_nonet', FloatCol(function = lg._als_nonet, entity = 'fam', label = u"Allocation logement sociale (non étudiant)")),
    build_simple_formula_couple('alset', FloatCol(function = lg._alset, entity = 'fam', label = u"Allocation logement sociale étudiante")),
    build_simple_formula_couple('apl', FloatCol(function = lg._apl, entity = 'fam', label = u"Aide personalisée au logement")),
    build_simple_formula_couple('crds_lgtm', FloatCol(function = lg._crds_lgtm, entity = 'fam', label = u"CRDS (allocation logement)")),
    build_simple_formula_couple('zone_apl', EnumCol(function = lg._zone_apl, default = 2, entity = 'men',
        enum = Enum([
            u"Non renseigné",
            u"Zone 1",
            u"Zone 2",
            u"Zone 3",
            ]),
        label = u"Zone APL",
        )),

    ############################################################
    # RSA/RMI
    ############################################################

    build_simple_formula_couple('div_ms', FloatCol(function = ms._div_ms)),
    build_simple_formula_couple('rfon_ms', FloatCol(function = ms._rfon_ms)),

    build_simple_formula_couple('ra_rsa', FloatCol(function = ms._ra_rsa, label = u"Revenus d'activité du Rsa")),
    build_simple_formula_couple('br_rmi_i', FloatCol(function = ms._br_rmi_i)),
    build_simple_formula_couple('br_rmi_ms', FloatCol(function = ms._br_rmi_ms)),
    build_simple_formula_couple('br_rmi_pf', FloatCol(function = ms._br_rmi_pf)),
    build_simple_formula_couple('br_rmi', FloatCol(function = ms._br_rmi, entity = 'fam', label = u"Base ressources du Rmi/Rsa")),

    build_simple_formula_couple('rmi_nbp', FloatCol(function = ms._rmi_nbp, entity = 'fam', label = u"Nombre de personne à charge au sens du Rmi/Rsa")),
    build_simple_formula_couple('forf_log', FloatCol(function = ms._forf_log, entity = 'fam')),
    build_simple_formula_couple('rsa_socle', FloatCol(function = ms._rsa_socle, entity = 'fam', label = u"RSA socle")),
    build_simple_formula_couple('rmi', FloatCol(function = ms._rmi, entity = 'fam', label = u"Revenu de solidarité active - socle")),
    build_simple_formula_couple('rsa', FloatCol(function = ms._rsa, entity = 'fam', label = u"Revenu de solidarité active")),
    build_simple_formula_couple('majo_rsa', FloatCol(function = ms._majo_rsa, entity = 'fam',
        label = u"Majoration pour parent isolé du Revenu de solidarité active socle", start = date(2009, 7, 1))),
    build_simple_formula_couple('rsa_act', FloatCol(function = ms._rsa_act, entity = 'fam', label = u"Revenu de solidarité active - activité", start = date(2009, 7, 1))),
    build_simple_formula_couple('rsa_act_i', FloatCol(function = ms._rsa_act_i)),
    build_simple_formula_couple('psa', FloatCol(function = ms._psa, entity = 'fam', label = u"Prime de solidarité active", start = date(2009, 1, 1), end = date(2009, 12, 31))),
    build_simple_formula_couple('api', FloatCol(function = ms._api, entity = 'fam', end = date(2009, 7, 1), label = u"Allocation de parent isolé")),
    build_simple_formula_couple('crds_mini', FloatCol(function = ms._crds_mini, entity = 'fam', start = date(2009, 7, 1))),
    build_simple_formula_couple('aefa', FloatCol(function = ms._aefa, entity = 'fam', label = u"Allocation exceptionnelle de fin d'année")),

    ############################################################
    # ASPA/ASI, Minimum vieillesse
    ############################################################

    build_simple_formula_couple('br_mv_i', FloatCol(function = ms._br_mv_i, label = u"Base ressources du minimum vieillesse/ASPA")),
    build_simple_formula_couple('br_mv', FloatCol(function = ms._br_mv, entity = 'fam', label = u"Base ressources du minimum vieillesse/ASPA")),

    build_simple_formula_couple('asi_aspa_nb_alloc', FloatCol(function = ms._asi_aspa_nb_alloc, entity = 'fam')),
    build_simple_formula_couple('asi_aspa_elig', BoolCol(function = ms._asi_aspa_elig, entity = 'fam')),
    build_simple_formula_couple('asi_elig', BoolCol(function = ms._asi_elig, label = u"Indicatrice individuelle d'éligibilité à l'allocation supplémentaire d'invalidité")),
    build_simple_formula_couple('asi_coexist_aspa', FloatCol(function = ms._asi_coexist_aspa, entity = 'fam', label = u"Allocation supplémentaire d'invalidité quand un adulte de la famille perçoit l'ASPA")),
    build_simple_formula_couple('asi_pure', FloatCol(function = ms._asi_pure, entity = 'fam', label = u"Allocation supplémentaire d'invalidité quand aucun adulte de la famille ne perçoit l'ASPA")),
    build_simple_formula_couple('asi', FloatCol(function = ms._asi, entity = 'fam', label = u"Allocation supplémentaire d'invalidité", start = date(2007, 1, 1))),
        # En 2007, Transformation du MV et de L'ASI en ASPA et ASI. La prestation ASPA calcule bien l'ancien MV
        # mais TODO manque l'ancienne ASI

    build_simple_formula_couple('aspa_elig', BoolCol(function = ms._aspa_elig, label = u"Indicatrice individuelle d'éligibilité à l'allocation de solidarité aux personnes agées")),
    build_simple_formula_couple('aspa_coexist_asi', FloatCol(function = ms._aspa_coexist_asi, entity = 'fam', label = u"Allocation de solidarité aux personnes agées quand un adulte de la famille perçoit l'ASI")),
    build_simple_formula_couple('aspa_pure', FloatCol(function = ms._aspa_pure, entity = 'fam', label = u"Allocation de solidarité aux personnes agées quand aucun adulte de la famille ne perçoit l'ASI")),
    build_simple_formula_couple('aspa', FloatCol(function = ms._aspa, entity = 'fam', label = u"Allocation de solidarité aux personnes agées")),

    ############################################################
    # Allocation adulte handicapé
    ############################################################

    build_simple_formula_couple('br_aah', FloatCol(function = ms._br_aah, entity = 'fam', label = u"Base ressources de l'allocation adulte handicapé")),
    build_simple_formula_couple('aah', FloatCol(function = ms._aah, entity = 'fam', label = u"Allocation adulte handicapé")),
    build_simple_formula_couple('caah', FloatCol(function = ms._caah, entity = 'fam', label = u"Complément de l'allocation adulte handicapé")),

    ############################################################
    # Taxe d'habitation
    ############################################################

    build_simple_formula_couple('tax_hab', FloatCol(function = th._tax_hab, entity = 'men', label = u"Taxe d'habitation")),

    ############################################################
    # Unité de consommation du ménage
    ############################################################
    build_simple_formula_couple('uc', FloatCol(function = cm._uc, entity = 'men', label = u"Unités de consommation")),

    ############################################################
    # Catégories
    ############################################################

    build_simple_formula_couple('typ_men', IntCol(function = cm._typ_men, entity = 'men', label = u"Type de ménage")),
    build_simple_formula_couple('nb_ageq0', IntCol(function = cl._nb_ageq0,
                           entity = 'men',
                           label = u"Effectifs des tranches d'âge quiquennal",
                           survey_only = True,
                           )),

    build_simple_formula_couple('nbinde', EnumCol(function = cl._nbinde,
                          label = u"Nombre d'individus dans le ménage", entity = 'men',
                          enum = Enum([u"Une personne",
                                       u"Deux personnes",
                                       u"Trois personnes",
                                       u"Quatre personnes",
                                       u"Cinq personnes",
                                       u"Six personnes et plus"], start = 1))),

     build_simple_formula_couple('cplx', BoolCol(function = cl._cplx, entity = 'men', label = u"Indicatrice de ménage complexe")),

     build_simple_formula_couple('act_cpl', IntCol(function = cl._act_cpl,
                           entity = 'men',
                           label = u"Nombre d'actifs parmi la personne de référence du méange et son conjoint")),

     build_simple_formula_couple('cohab', BoolCol(function = cl._cohab,
                          entity = 'men',
                          label = u"Vie en couple")),

     build_simple_formula_couple('act_enf', IntCol(function = cl._act_enf, entity = 'men',
                           label = u"Nombre d'enfants actifs")),

     build_simple_formula_couple('typmen15', EnumCol(function = cl._typmen15, label = u"Type de ménage", entity = 'men',
                           enum = Enum([u"Personne seule active",
                                        u"Personne seule inactive",
                                        u"Familles monoparentales, parent actif",
                                        u"Familles monoparentales, parent inactif et au moins un enfant actif",
                                        u"Familles monoparentales, tous inactifs",
                                        u"Couples sans enfant, 1 actif",
                                        u"Couples sans enfant, 2 actifs",
                                        u"Couples sans enfant, tous inactifs",
                                        u"Couples avec enfant, 1 membre du couple actif",
                                        u"Couples avec enfant, 2 membres du couple actif",
                                        u"Couples avec enfant, couple inactif et au moins un enfant actif",
                                        u"Couples avec enfant, tous inactifs",
                                        u"Autres ménages, 1 actif",
                                        u"Autres ménages, 2 actifs ou plus",
                                        u"Autres ménages, tous inactifs"], start = 1))),

     build_simple_formula_couple('decile', EnumCol(function = cm._decile,
                           entity = 'men',
                           label = u"Décile de niveau de vie disponible",
                           enum = Enum([u"Hors champ"
                                          u"1er décile",
                                          u"2nd décile",
                                          u"3e décile",
                                          u"4e décile",
                                          u"5e décile",
                                          u"6e décile",
                                          u"7e décile",
                                          u"8e décile",
                                          u"9e décile",
                                          u"10e décile"]),
                           survey_only = True,
                           )),

     build_simple_formula_couple('decile_net', EnumCol(function = cm._decile_net,
                               entity = 'men',
                               label = u"Décile de niveau de vie net",
                               enum = Enum([u"Hors champ"
                                            u"1er décile",
                                            u"2nd décile",
                                            u"3e décile",
                                            u"4e décile",
                                            u"5e décile",
                                            u"6e décile",
                                            u"7e décile",
                                            u"8e décile",
                                            u"9e décile",
                                            u"10e décile"]),
                               survey_only = True,
                               )),

     build_simple_formula_couple('pauvre40', EnumCol(function = cm._pauvre40,
                             entity = 'men',
                             label = u"Pauvreté monétaire au seuil de 40%",
                             enum = Enum([u"Ménage au dessus du seuil de pauvreté à 40%",
                                          u"Ménage en dessous du seuil de pauvreté à 40%"]),
                             survey_only = True,
                             )),

     build_simple_formula_couple('pauvre50', EnumCol(function = cm._pauvre50,
                             entity = 'men',
                             label = u"Pauvreté monétaire au seuil de 50%",
                             enum = Enum([u"Ménage au dessus du seuil de pauvreté à 50%",
                                          u"Ménage en dessous du seuil de pauvreté à 50%"]),
                             survey_only = True,
                             )),

     build_simple_formula_couple('pauvre60', EnumCol(function = cm._pauvre60,
                             entity = 'men',
                             label = u"Pauvreté monétaire au seuil de 60%",
                             enum = Enum([u"Ménage au dessus du seuil de pauvreté à 50%",
                                          u"Ménage en dessous du seuil de pauvreté à 50%"]),
                             survey_only = True,
                             )),

    ############################################################
    # Totaux
    ############################################################

    build_simple_formula_couple('revdisp', FloatCol(function = cm._revdisp, entity = 'men', label = u"Revenu disponible du ménage")),
    build_simple_formula_couple('nivvie', FloatCol(function = cm._nivvie, entity = 'men', label = u"Niveau de vie du ménage")),

    build_simple_formula_couple('revnet', FloatCol(function = cm._revnet, entity = 'men', label = u"Revenu net du ménage")),
    build_simple_formula_couple('nivvie_net', FloatCol(function = cm._nivvie_net, entity = 'men', label = u"Niveau de vie net du ménage")),

    build_simple_formula_couple('revini', FloatCol(function = cm._revini, entity = 'men', label = u"Revenu initial du ménage")),
    build_simple_formula_couple('nivvie_ini', FloatCol(function = cm._nivvie_ini, entity = 'men', label = u"Niveau de vie initial du ménage")),

    build_simple_formula_couple('rev_trav', FloatCol(function = cm._rev_trav, label = u"Revenus du travail (salariés et non salariés)")),
    build_simple_formula_couple('pen', FloatCol(function = cm._pen, label = u"Total des pensions et revenus de remplacement")),
    build_simple_formula_couple('cotsoc_bar', FloatCol(function = cm._cotsoc_bar, label = u"Cotisations sociales sur les revenus du capital imposés au barème")),
    build_simple_formula_couple('cotsoc_lib', FloatCol(function = cm._cotsoc_lib, label = u"Cotisations sociales sur les revenus du capital soumis au prélèvement libératoire")),
    build_simple_formula_couple('rev_cap', FloatCol(function = cm._rev_cap, label = u"Revenus du patrimoine")),
    build_simple_formula_couple('psoc', FloatCol(function = cm._psoc, entity = 'fam', label = u"Total des prestations sociales")),
    build_simple_formula_couple('prelsoc_cap', FloatCol(function = cm._prelsoc_cap, label = u"Prélèvements sociaux sur les revenus du capital")),
    build_simple_formula_couple('pfam', FloatCol(function = cm._pfam, entity = 'fam', label = u"Total des prestations familiales")),
    build_simple_formula_couple('mini', FloatCol(function = cm._mini, entity = 'fam', label = u"Minima sociaux")),
    build_simple_formula_couple('logt', FloatCol(function = cm._logt, entity = 'fam', label = u"Allocations logements")),
    build_simple_formula_couple('impo', FloatCol(function = cm._impo, entity = 'men', label = u"Impôts sur le revenu")),
    build_simple_formula_couple('crds', FloatCol(function = cm._crds, label = u"Total des contributions au remboursement de la dette sociale")),
    build_simple_formula_couple('csg', FloatCol(function = cm._csg, label = u"Total des contributions sociale généralisée")),
    build_simple_formula_couple('cotsoc_noncontrib', FloatCol(function = cm._cotsoc_noncontrib, label = u"Cotisations sociales non contributives")),
    build_simple_formula_couple('check_csk', FloatCol(function = cm._check_csk, entity = 'men')),
    build_simple_formula_couple('check_csg', FloatCol(function = cm._check_csg, entity = 'men')),
    build_simple_formula_couple('check_crds', FloatCol(function = cm._check_crds, entity = 'men')),

    ))