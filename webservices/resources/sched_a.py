import sqlalchemy as sa
from flask_apispec import doc
import re

from webservices import args
from webservices import docs
from webservices import utils
from webservices import filters
from webservices import schemas
from webservices.common import models
from webservices.common import views
from webservices.common.views import ItemizedResource
from webservices import exceptions


@doc(
    tags=['receipts'],
    description=docs.SCHEDULE_A,
)
class ScheduleAView(ItemizedResource):

    model = models.ScheduleA
    schema = schemas.ScheduleASchema
    page_schema = schemas.ScheduleAPageSchema

    @property
    def year_column(self):
        return self.model.two_year_transaction_period
    @property
    def index_column(self):
        return self.model.sub_id
    @property
    def amount_column(self):
        return self.model.contribution_receipt_amount
    filter_multi_fields = [
        ('image_number', models.ScheduleA.image_number),
        ('committee_id', models.ScheduleA.committee_id),
        ('contributor_id', models.ScheduleA.contributor_id),
        ('contributor_city', models.ScheduleA.contributor_city),
        ('contributor_state', models.ScheduleA.contributor_state),
    ]
    filter_match_fields = [
        ('is_individual', models.ScheduleA.is_individual),
        ('two_year_transaction_period', models.ScheduleA.two_year_transaction_period),
    ]
    filter_range_fields = [
        (('min_date', 'max_date'), models.ScheduleA.contribution_receipt_date),
        (('min_amount', 'max_amount'), models.ScheduleA.contribution_receipt_amount),
        (('min_image_number', 'max_image_number'), models.ScheduleA.image_number),
    ]
    filter_fulltext_fields = [
        ('contributor_name', models.ScheduleA.contributor_name_text),
        ('contributor_employer', models.ScheduleA.contributor_employer_text),
        ('contributor_occupation', models.ScheduleA.contributor_occupation_text),
    ]
    filter_multi_start_with_fields = [
        ('contributor_zip', models.ScheduleA.contributor_zip),
    ]
    query_options = [
        sa.orm.joinedload(models.ScheduleA.committee),
        sa.orm.joinedload(models.ScheduleA.contributor),
    ]

    @property
    def args(self):
        return utils.extend(
            args.itemized,
            args.schedule_a,
            args.make_seek_args(),
            args.make_sort_args(
                default='contribution_receipt_date',
                validator=args.OptionValidator([
                    'contribution_receipt_date',
                    'contribution_receipt_amount',
                    'contributor_aggregate_ytd',
                ]),
            )
        )

    def build_query(self, **kwargs):
        query = super().build_query(**kwargs)
        query = filters.filter_contributor_type(query, self.model.entity_type, kwargs)

        if kwargs.get('contributor_zip'):
            for value in kwargs['contributor_zip']:
                if re.search('^-?\d{5}$',value) is None:
                    raise exceptions.ApiError(
                        'Invalid Zip code. It must be 5 digits',
                        status_code=400,
                    )
            query = filters.filter_multi_start_with(query, kwargs, self.filter_multi_start_with_fields)
        
        if kwargs.get('sub_id'):
            query = query.filter_by(sub_id= int(kwargs.get('sub_id')))
        if kwargs.get('line_number'):
            if len(kwargs.get('line_number').split('-')) == 2:
                form, line_no = kwargs.get('line_number').split('-')
                query = query.filter_by(filing_form=form.upper())
                query = query.filter_by(line_number=line_no)
        return query

@doc(
    tags=['receipts'],
    description=docs.EFILING_TAG,
)
class ScheduleAEfileView(views.ApiResource):
    model = models.ScheduleAEfile
    schema = schemas.ItemizedScheduleAfilingsSchema
    page_schema = schemas.ScheduleAEfilePageSchema

    filter_multi_fields = [
        ('image_number', models.ScheduleAEfile.image_number),
        ('committee_id', models.ScheduleAEfile.committee_id),
        ('contributor_city', models.ScheduleAEfile.contributor_city),
        ('contributor_state', models.ScheduleAEfile.contributor_state),
        #('contributor_name', models.ScheduleAEfile.contr)
    ]

    filter_range_fields = [
        (('min_date', 'max_date'), models.ScheduleAEfile.contribution_receipt_date),
        (('min_amount', 'max_amount'), models.ScheduleAEfile.contribution_receipt_amount),
        (('min_image_number', 'max_image_number'), models.ScheduleAEfile.image_number),
    ]

    filter_fulltext_fields = [
        ('contributor_name', models.ScheduleAEfile.contributor_name_text),
        ('contributor_employer', models.ScheduleAEfile.contributor_employer_text),
        ('contributor_occupation', models.ScheduleAEfile.contributor_occupation_text),
    ]

    @property
    def args(self):
        return utils.extend(
            args.paging,
            args.schedule_a_e_file,
            args.itemized,
            args.make_sort_args(
                default='-contribution_receipt_date',
                validator=args.OptionValidator([
                    'contribution_receipt_date',
                    'contribution_receipt_amount',
                    'contributor_aggregate_ytd',
                ]),
            ),
        )

