from restful_resources.account import AccountsApi, DistinctAccountTypesApi
from restful_resources.categories import CategoriesApi, CategoryStatsApi
from restful_resources.stats import MonthStatsApi, InExStatsApi
from restful_resources.transactions import TransactionsListApi, AddTransactionApi, FundTransactionsApi, GetDescriptionSuggestionsApi


def initialize_routes(api):
    api.add_resource(AccountsApi, '/api/accounts')
    api.add_resource(CategoriesApi, '/api/categories')
    api.add_resource(DistinctAccountTypesApi, '/api/distinctaccounts')
    api.add_resource(TransactionsListApi, '/api/listtransactions')
    api.add_resource(AddTransactionApi, '/api/addtransaction')
    api.add_resource(FundTransactionsApi, '/api/fundtransfer')
    api.add_resource(MonthStatsApi, '/api/monthstats')
    api.add_resource(GetDescriptionSuggestionsApi, '/api/descriptionsuggestions')
    api.add_resource(CategoryStatsApi, '/api/categorystats')
    api.add_resource(InExStatsApi, '/api/inexstats')
