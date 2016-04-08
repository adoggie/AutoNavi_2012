import pyamf
from pyamf.flex import ArrayCollection, ObjectProxy
from pyamf.remoting.gateway.django import DjangoGateway
#from giscore.models import AO_Group
import server


#pyamf.register_class(AO_Group, 'com.subscription.vos.SubscriberVO')


s = server.MainService.instance()

print s
services = {
	#'tax.login':s.login,
	#'tax.syslogout':s.logout,
	'tax.billMerge':s.billMerge,
	'tax.billSplit':s.billSplit,
	'tax.billUnMerge':s.billUnMerge,
	'tax.billUnSplit':s.billUnSplit,
	'tax.createClient':s.createClient,
	'tax.createGoods':s.createGoods,
	'tax.deleteBill':s.deleteBill,
	'tax.deleteClient':s.deleteClient,
	'tax.deleteGoods':s.deleteGoods,
	'tax.exportInvoiceList':s.exportInvoiceList,
	'tax.getBillItemList':s.getBillItemList,
	'tax.getBillList':s.getBillList,
	'tax.getClientList':s.getClientList,
	'tax.getGoodsList':s.getGoodsList,
	'tax.getInvoiceItemList':s.getInvoiceItemList,
	'tax.getInvoiceList':s.getInvoiceList,
	'tax.getSystemParamList':s.getSystemParamList,
	'tax.getSystemParameter':s.getSystemParameter,
	'tax.printInvoice':s.printInvoice,
	'tax.destroyInvoice':s.destroyInvoice,
	'tax.printInvoiceItems':s.printInvoiceItems,
	'tax.readTaxCardInfo':s.readTaxCardInfo,
	'tax.setSystemParameters':s.setSystemParameters,
	'tax.updateClient':s.updateClient,
	'tax.updateGoods':s.updateGoods,
	'tax.genInvoice':s.genInvoice,
	'tax.exportBillList':s.exportBillList,
	'tax.importBills':s.importBills,
	'tax.updateBillMemo':s.updateBillMemo,
	'tax.splitProduct':s.splitProduct,
	'tax.discardProduct':s.discardProduct,
	'tax.createBillFromProducts':s.createBillFromProducts,
	'tax.billDiscard':s.billDiscard,
	'tax.generateInvoice':s.generateInvoice,
	'tax.openTaxCard':s.openTaxCard,
	'tax.closeTaxCard':s.closeTaxCard,
	'tax.billUpdateMemo':s.billUpdateMemo,
	'tax.invoiceWriteBack':s.invoiceWriteBack,
	'tax.backupSystemDB':s.backupSystemDB,
	'tax.exportClients':s.exportClients,
	'tax.exportGoods':s.exportGoods,
	'tax.printInvoicePrepare':s.printInvoicePrepare,
	'tax.printInvoiceList':s.printInvoiceList,
	
	#---------------------------------------------------------------------------
}

gateway = DjangoGateway(services, expose_request=True)

if __name__=='__main__':
	import sys
	sys.exit()